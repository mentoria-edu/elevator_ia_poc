"""Testes unitários do motor do elevador."""

import pytest

from elevator_vibe_code.elevator import Elevator
from elevator_vibe_code.models import (
    Direction,
    ElevatorEvent,
    EventKind,
    Floor,
    Passenger,
    ServicePhase,
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


def make_upward_phase(
    destinations: tuple[int, ...] = (2,),
) -> ServicePhase:
    """Cria uma fase de subida determinística."""
    requests = tuple(
        make_passenger(f"up-{index}", 0, destination)
        for index, destination in enumerate(destinations)
    )
    return ServicePhase(direction=Direction.UP, requests=requests)


def make_downward_phase(
    origins: tuple[int, ...] = (5,),
) -> ServicePhase:
    """Cria uma fase de descida com origens individuais."""
    requests = tuple(
        make_passenger(f"down-{index}", origin, 0)
        for index, origin in enumerate(origins)
    )
    return ServicePhase(direction=Direction.DOWN, requests=requests)


def event_kinds(
    events: tuple[ElevatorEvent, ...],
) -> tuple[EventKind, ...]:
    """Retorna os tipos dos eventos produzidos."""
    return tuple(event.kind for event in events)


def run_by_steps(elevator: Elevator) -> tuple[ElevatorEvent, ...]:
    """Avança uma fase até o snapshot terminal."""
    events: list[ElevatorEvent] = []
    while not elevator.snapshot().is_idle:
        events.extend(elevator.step())
    return tuple(events)


def test_new_elevator_is_idle_on_ground_by_default() -> None:
    elevator = Elevator()

    snapshot = elevator.snapshot()

    assert snapshot.current_floor == Floor(0)
    assert snapshot.direction is Direction.IDLE
    assert snapshot.cabin == ()
    assert snapshot.upward_waiting == ()
    assert snapshot.downward_waiting == ()
    assert snapshot.elapsed_seconds == 0
    assert snapshot.is_idle
    assert elevator.step() == ()


def test_first_step_boards_upward_requests_in_fifo_order() -> None:
    elevator = Elevator()
    phase = make_upward_phase((2, 4, 3))
    elevator.start_phase(phase)

    events = elevator.step()

    assert event_kinds(events) == (
        EventKind.ARRIVAL,
        EventKind.DOOR_OPENING,
        EventKind.PASSENGERS_ENTERED,
        EventKind.DOOR_CLOSING,
    )
    assert events[2].passengers == phase.requests
    snapshot = elevator.snapshot()
    assert snapshot.cabin == phase.requests
    assert snapshot.upward_waiting == ()
    assert snapshot.elapsed_seconds == 2
    assert snapshot.direction is Direction.UP


def test_each_traversed_floor_produces_one_movement_event() -> None:
    elevator = Elevator()
    elevator.start_phase(make_upward_phase((3,)))
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
        EventKind.IDLE,
    )
    assert floor_one_events[0].floor == Floor(1)
    assert floor_two_events[0].floor == Floor(2)
    assert {event.floor for event in floor_three_events} == {Floor(3)}


def test_phase_never_exceeds_capacity() -> None:
    elevator = Elevator()
    phase = make_upward_phase((10, 10, 10, 10, 10, 10))
    elevator.start_phase(phase)

    elevator.step()

    assert elevator.snapshot().cabin == phase.requests
    assert len(elevator.snapshot().cabin) == 6


def test_same_floor_downward_requests_board_in_fifo_order() -> None:
    elevator = Elevator(initial_floor=Floor(10))
    phase = make_downward_phase((8, 5, 8))
    elevator.start_phase(phase)

    assert event_kinds(elevator.step()) == (EventKind.FLOOR_PASSED,)
    floor_eight_events = elevator.step()

    assert event_kinds(floor_eight_events) == (
        EventKind.ARRIVAL,
        EventKind.DOOR_OPENING,
        EventKind.PASSENGERS_ENTERED,
        EventKind.DOOR_CLOSING,
    )
    assert floor_eight_events[2].passengers == (
        phase.requests[0],
        phase.requests[2],
    )
    assert elevator.snapshot().downward_waiting == (phase.requests[1],)

    events = elevator.run_until_idle()

    entered = tuple(
        passenger
        for event in events
        if event.kind is EventKind.PASSENGERS_ENTERED
        for passenger in event.passengers
    )
    assert entered == (phase.requests[1],)
    assert elevator.snapshot().current_floor == Floor(0)


@pytest.mark.parametrize(
    ("origins", "expected_direction", "expected_floor"),
    [
        ((7, 13), Direction.DOWN, Floor(9)),
        ((13, 7), Direction.UP, Floor(11)),
    ],
)
def test_nearest_request_uses_fifo_to_break_distance_ties(
    origins: tuple[int, ...],
    expected_direction: Direction,
    expected_floor: Floor,
) -> None:
    elevator = Elevator(initial_floor=Floor(10))
    elevator.start_phase(make_downward_phase(origins))

    events = elevator.step()

    assert event_kinds(events) == (EventKind.FLOOR_PASSED,)
    assert events[0].direction is expected_direction
    assert events[0].floor == expected_floor


def test_empty_elevator_changes_direction_after_upward_trip_to_down_call() -> (
    None
):
    elevator = Elevator(initial_floor=Floor(2))
    phase = make_downward_phase((4,))
    elevator.start_phase(phase)

    elevator.step()
    events = elevator.step()

    assert event_kinds(events) == (
        EventKind.ARRIVAL,
        EventKind.DOOR_OPENING,
        EventKind.PASSENGERS_ENTERED,
        EventKind.DOOR_CLOSING,
        EventKind.DIRECTION_CHANGED,
    )
    assert events[2].passengers == phase.requests
    assert events[-1].direction is Direction.DOWN


def test_new_phase_is_rejected_while_previous_phase_is_active() -> None:
    elevator = Elevator()
    elevator.start_phase(make_upward_phase())

    with pytest.raises(RuntimeError, match="fase anterior"):
        elevator.start_phase(make_downward_phase())


def test_downward_phase_starts_where_upward_phase_finished() -> None:
    elevator = Elevator()
    elevator.start_phase(make_upward_phase((4,)))
    elevator.run_until_idle()
    upward_snapshot = elevator.snapshot()

    elevator.start_phase(make_downward_phase((3,)))
    first_downward_events = elevator.step()

    assert upward_snapshot.current_floor == Floor(4)
    assert first_downward_events[0].floor == Floor(3)
    assert first_downward_events[0].kind is EventKind.ARRIVAL
    assert (
        first_downward_events[0].elapsed_seconds
        == upward_snapshot.elapsed_seconds + 1
    )

    elevator.run_until_idle()
    final_snapshot = elevator.snapshot()
    assert final_snapshot.current_floor == Floor(0)
    assert final_snapshot.elapsed_seconds > upward_snapshot.elapsed_seconds


@pytest.mark.parametrize(
    ("initial_floor", "phase"),
    [
        (Floor(0), make_upward_phase((2, 4))),
        (Floor(10), make_downward_phase((8, 5, 8))),
    ],
)
def test_step_and_run_until_idle_produce_equivalent_events_per_phase(
    initial_floor: Floor,
    phase: ServicePhase,
) -> None:
    stepped_elevator = Elevator(initial_floor=initial_floor)
    running_elevator = Elevator(initial_floor=initial_floor)
    stepped_elevator.start_phase(phase)
    running_elevator.start_phase(phase)

    stepped_events = run_by_steps(stepped_elevator)

    assert stepped_events == running_elevator.run_until_idle()
    assert stepped_elevator.snapshot() == running_elevator.snapshot()


def test_snapshot_does_not_expose_mutable_internal_collections() -> None:
    elevator = Elevator()
    elevator.start_phase(make_upward_phase((2, 3)))
    before_step = elevator.snapshot()

    elevator.step()

    assert isinstance(before_step.upward_waiting, tuple)
    assert len(before_step.upward_waiting) == 2
    assert elevator.snapshot().upward_waiting == ()


def test_idle_event_keeps_last_attended_floor_and_empty_state() -> None:
    elevator = Elevator(initial_floor=Floor(6))
    elevator.start_phase(make_downward_phase((5, 3)))

    events = elevator.run_until_idle()
    snapshot = elevator.snapshot()

    assert events[-1].kind is EventKind.IDLE
    assert events[-1].direction is Direction.IDLE
    assert snapshot.current_floor == Floor(0)
    assert snapshot.direction is Direction.IDLE
    assert snapshot.cabin == ()
    assert snapshot.upward_waiting == ()
    assert snapshot.downward_waiting == ()
    assert snapshot.is_idle
