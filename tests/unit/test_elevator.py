"""Testes unitários do motor do elevador."""

import pytest

from elevator_vibe_code.elevator import Elevator
from elevator_vibe_code.models import (
    Direction,
    ElevatorCall,
    ElevatorEvent,
    EventKind,
    Floor,
    Passenger,
    ServiceRound,
)


def make_passenger(
    passenger_id: str,
    origin: int,
    destination: int,
) -> Passenger:
    """Cria um passageiro válido com nome identificável."""
    direction = Direction.UP if destination > origin else Direction.DOWN
    return Passenger(
        passenger_id=passenger_id,
        name=f"Pessoa {passenger_id}",
        origin=Floor(origin),
        destination=Floor(destination),
        direction=direction,
    )


def make_round(
    upward_destinations: tuple[int, ...] = (2,),
    *,
    downward_floor: int = 5,
    downward_count: int = 1,
) -> ServiceRound:
    """Cria uma rodada determinística com as duas chamadas obrigatórias."""
    upward_passengers = tuple(
        make_passenger(f"up-{index}", 0, destination)
        for index, destination in enumerate(upward_destinations)
    )
    downward_passengers = tuple(
        make_passenger(f"down-{index}", downward_floor, 0)
        for index in range(downward_count)
    )
    return ServiceRound(
        upward_call=ElevatorCall(
            floor=Floor(0),
            direction=Direction.UP,
            passengers=upward_passengers,
        ),
        downward_call=ElevatorCall(
            floor=Floor(downward_floor),
            direction=Direction.DOWN,
            passengers=downward_passengers,
        ),
    )


def event_kinds(
    events: tuple[ElevatorEvent, ...],
) -> tuple[EventKind, ...]:
    """Retorna os tipos dos eventos produzidos."""
    return tuple(event.kind for event in events)


def test_new_elevator_is_idle_on_ground_by_default() -> None:
    elevator = Elevator()

    snapshot = elevator.snapshot()

    assert snapshot.current_floor == Floor(0)
    assert snapshot.direction is Direction.IDLE
    assert snapshot.cabin == ()
    assert snapshot.elapsed_seconds == 0
    assert snapshot.is_idle
    assert elevator.step() == ()


def test_first_step_boards_upward_queue_in_fifo_order() -> None:
    elevator = Elevator()
    service_round = make_round((2, 4, 3))
    elevator.start_round(service_round)

    events = elevator.step()

    assert event_kinds(events) == (
        EventKind.ARRIVAL,
        EventKind.DOOR_OPENING,
        EventKind.PASSENGERS_ENTERED,
        EventKind.DOOR_CLOSING,
    )
    assert events[2].passengers == service_round.upward_call.passengers
    snapshot = elevator.snapshot()
    assert snapshot.cabin == service_round.upward_call.passengers
    assert snapshot.upward_waiting == ()
    assert snapshot.elapsed_seconds == 2
    assert snapshot.direction is Direction.UP


def test_each_traversed_floor_produces_one_movement_event() -> None:
    elevator = Elevator()
    elevator.start_round(make_round((3,), downward_floor=5))
    elevator.step()

    floor_one_events = elevator.step()
    floor_two_events = elevator.step()
    floor_three_events = elevator.step()

    assert event_kinds(floor_one_events) == (EventKind.FLOOR_PASSED,)
    assert event_kinds(floor_two_events) == (EventKind.FLOOR_PASSED,)
    assert event_kinds(floor_three_events) == (
        EventKind.ARRIVAL,
        EventKind.DOOR_OPENING,
        EventKind.PASSENGERS_EXITED,
        EventKind.DOOR_CLOSING,
    )
    assert [event.floor.number for event in floor_one_events] == [1]
    assert [event.floor.number for event in floor_two_events] == [2]
    assert {event.floor.number for event in floor_three_events} == {3}


def test_full_cabin_passes_opposite_queue_without_opening_door() -> None:
    elevator = Elevator()
    elevator.start_round(
        make_round((10, 10, 10, 10, 10, 10), downward_floor=5)
    )
    elevator.step()

    events_by_floor: dict[int, tuple[ElevatorEvent, ...]] = {}
    for _ in range(5):
        events = elevator.step()
        events_by_floor[events[0].floor.number] = events

    assert event_kinds(events_by_floor[5]) == (EventKind.FLOOR_PASSED,)
    snapshot = elevator.snapshot()
    assert snapshot.current_floor == Floor(5)
    assert len(snapshot.cabin) == 6
    assert len(snapshot.downward_waiting) == 1


def test_opposite_queue_at_destination_waits_for_empty_cabin() -> None:
    elevator = Elevator()
    service_round = make_round((5, 8), downward_floor=5)
    elevator.start_round(service_round)
    elevator.step()
    for _ in range(4):
        elevator.step()

    events = elevator.step()

    assert event_kinds(events) == (
        EventKind.ARRIVAL,
        EventKind.DOOR_OPENING,
        EventKind.PASSENGERS_EXITED,
        EventKind.DOOR_CLOSING,
    )
    snapshot = elevator.snapshot()
    assert tuple(
        passenger.destination.number for passenger in snapshot.cabin
    ) == (8,)
    assert snapshot.downward_waiting == (
        service_round.downward_call.passengers[0],
    )
    assert snapshot.direction is Direction.UP


def test_exit_precedes_opposite_entry_and_direction_change() -> None:
    elevator = Elevator()
    service_round = make_round((5,), downward_floor=5)
    elevator.start_round(service_round)
    elevator.step()
    for _ in range(4):
        elevator.step()

    events = elevator.step()

    assert event_kinds(events) == (
        EventKind.ARRIVAL,
        EventKind.DOOR_OPENING,
        EventKind.PASSENGERS_EXITED,
        EventKind.PASSENGERS_ENTERED,
        EventKind.DOOR_CLOSING,
        EventKind.DIRECTION_CHANGED,
    )
    assert events[2].passengers == service_round.upward_call.passengers
    assert events[3].passengers == service_round.downward_call.passengers
    assert events[-1].direction is Direction.DOWN


def test_door_time_is_added_without_extra_boarding_time() -> None:
    elevator = Elevator()
    elevator.start_round(make_round((2,), downward_floor=2))

    ground_events = elevator.step()
    floor_one_events = elevator.step()
    floor_two_events = elevator.step()

    assert [event.elapsed_seconds for event in ground_events] == [0, 1, 1, 2]
    assert [event.elapsed_seconds for event in floor_one_events] == [3]
    assert [event.elapsed_seconds for event in floor_two_events] == [
        4,
        5,
        5,
        5,
        6,
        6,
    ]


def test_nearest_call_is_chosen_when_cabin_is_empty() -> None:
    elevator = Elevator(initial_floor=Floor(10))
    elevator.start_round(make_round((2,), downward_floor=17))

    events = elevator.step()

    assert event_kinds(events) == (EventKind.FLOOR_PASSED,)
    assert events[0].floor == Floor(11)
    assert events[0].direction is Direction.UP


def test_upward_call_wins_equal_distance_tie() -> None:
    elevator = Elevator(initial_floor=Floor(5))
    elevator.start_round(make_round((2,), downward_floor=10))

    events = elevator.step()

    assert event_kinds(events) == (EventKind.FLOOR_PASSED,)
    assert events[0].floor == Floor(4)
    assert events[0].direction is Direction.DOWN


def test_new_round_is_rejected_while_previous_round_is_active() -> None:
    elevator = Elevator()
    elevator.start_round(make_round())

    with pytest.raises(RuntimeError, match="rodada anterior"):
        elevator.start_round(make_round((3,), downward_floor=6))


def test_successive_round_is_accepted_after_idle() -> None:
    elevator = Elevator()
    elevator.start_round(make_round((1,), downward_floor=1))
    first_events = elevator.run_until_idle()

    elevator.start_round(make_round((2,), downward_floor=2))
    second_events = elevator.run_until_idle()

    assert first_events[-1].kind is EventKind.IDLE
    assert second_events[-1].kind is EventKind.IDLE
    assert elevator.snapshot().is_idle


def test_step_and_run_until_idle_produce_equivalent_events() -> None:
    service_round = make_round((2, 4), downward_floor=6)
    stepped_elevator = Elevator()
    running_elevator = Elevator()
    stepped_elevator.start_round(service_round)
    running_elevator.start_round(service_round)

    stepped_events: list[ElevatorEvent] = []
    while not stepped_elevator.snapshot().is_idle:
        stepped_events.extend(stepped_elevator.step())

    assert tuple(stepped_events) == running_elevator.run_until_idle()
    assert stepped_elevator.snapshot() == running_elevator.snapshot()


def test_snapshot_does_not_expose_mutable_internal_collections() -> None:
    elevator = Elevator()
    elevator.start_round(make_round((2, 3), downward_floor=4))
    before_step = elevator.snapshot()

    elevator.step()

    assert isinstance(before_step.upward_waiting, tuple)
    assert len(before_step.upward_waiting) == 2
    assert elevator.snapshot().upward_waiting == ()


def test_idle_event_keeps_last_attended_floor() -> None:
    elevator = Elevator()
    elevator.start_round(make_round((1,), downward_floor=1))

    events = elevator.run_until_idle()
    snapshot = elevator.snapshot()

    assert events[-1].kind is EventKind.IDLE
    assert events[-1].direction is Direction.IDLE
    assert snapshot.current_floor == Floor(0)
    assert snapshot.direction is Direction.IDLE
    assert snapshot.is_idle
