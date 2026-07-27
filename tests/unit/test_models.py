"""Testes dos modelos imutáveis do elevador."""

from dataclasses import FrozenInstanceError

import pytest

from elevator_vibe_code.models import (
    ELEVATOR_CAPACITY,
    GROUND_FLOOR_NUMBER,
    TOP_FLOOR_NUMBER,
    Direction,
    ElevatorCall,
    ElevatorEvent,
    ElevatorSnapshot,
    EventKind,
    Floor,
    Passenger,
    ServiceRound,
)


def _upward_passenger(
    passenger_id: str = "up-1",
    destination: int = 4,
) -> Passenger:
    return Passenger(
        passenger_id=passenger_id,
        name="Ana Souza",
        origin=Floor(GROUND_FLOOR_NUMBER),
        destination=Floor(destination),
        direction=Direction.UP,
    )


def _downward_passenger(
    passenger_id: str = "down-1",
    origin: int = 9,
) -> Passenger:
    return Passenger(
        passenger_id=passenger_id,
        name="Carlos Lima",
        origin=Floor(origin),
        destination=Floor(GROUND_FLOOR_NUMBER),
        direction=Direction.DOWN,
    )


def _valid_calls() -> tuple[ElevatorCall, ElevatorCall]:
    upward_passenger = _upward_passenger()
    downward_passenger = _downward_passenger()
    return (
        ElevatorCall(
            floor=upward_passenger.origin,
            direction=Direction.UP,
            passengers=(upward_passenger,),
        ),
        ElevatorCall(
            floor=downward_passenger.origin,
            direction=Direction.DOWN,
            passengers=(downward_passenger,),
        ),
    )


def test_public_constants_and_enum_values_match_contract() -> None:
    assert GROUND_FLOOR_NUMBER == 0
    assert TOP_FLOOR_NUMBER == 17
    assert ELEVATOR_CAPACITY == 6
    assert [direction.value for direction in Direction] == [
        "SUBINDO",
        "DESCENDO",
        "PARADO",
    ]
    assert [kind.value for kind in EventKind] == [
        "floor_passed",
        "arrival",
        "door_opening",
        "passengers_exited",
        "passengers_entered",
        "door_closing",
        "direction_changed",
        "idle",
    ]


def test_floor_accepts_boundaries_and_supports_ordering() -> None:
    ground_floor = Floor(GROUND_FLOOR_NUMBER)
    top_floor = Floor(TOP_FLOOR_NUMBER)

    assert ground_floor < top_floor
    assert sorted((top_floor, ground_floor)) == [ground_floor, top_floor]
    assert not hasattr(ground_floor, "__dict__")


@pytest.mark.parametrize("number", [-1, 18])
def test_floor_rejects_numbers_outside_building(number: int) -> None:
    with pytest.raises(ValueError, match="Número de andar inválido"):
        Floor(number)


def test_floor_rejects_boolean() -> None:
    with pytest.raises(ValueError, match="Esperado um inteiro"):
        Floor(True)


@pytest.mark.parametrize("number", [1.5, "1", None])
def test_floor_rejects_non_integer(number: object) -> None:
    with pytest.raises(ValueError, match="Esperado um inteiro"):
        Floor(number)  # type: ignore[arg-type]


def test_passenger_accepts_upward_and_downward_trips() -> None:
    upward_passenger = _upward_passenger()
    downward_passenger = _downward_passenger()

    assert upward_passenger.direction is Direction.UP
    assert downward_passenger.direction is Direction.DOWN


@pytest.mark.parametrize(
    ("origin", "destination", "direction"),
    [
        (0, 0, Direction.UP),
        (4, 4, Direction.DOWN),
        (3, 8, Direction.UP),
        (0, 5, Direction.DOWN),
        (8, 0, Direction.UP),
        (0, 5, Direction.IDLE),
    ],
)
def test_passenger_rejects_invalid_trip(
    origin: int,
    destination: int,
    direction: Direction,
) -> None:
    with pytest.raises(ValueError, match="Viagem inválida"):
        Passenger(
            passenger_id="invalid",
            name="Pessoa Inválida",
            origin=Floor(origin),
            destination=Floor(destination),
            direction=direction,
        )


def test_elevator_call_accepts_passengers_in_fifo_order() -> None:
    first_passenger = _upward_passenger("first", destination=2)
    second_passenger = _upward_passenger("second", destination=8)

    elevator_call = ElevatorCall(
        floor=Floor(GROUND_FLOOR_NUMBER),
        direction=Direction.UP,
        passengers=(first_passenger, second_passenger),
    )

    assert elevator_call.passengers == (first_passenger, second_passenger)


def test_elevator_call_rejects_empty_queue() -> None:
    with pytest.raises(ValueError, match="Quantidade de passageiros inválida"):
        ElevatorCall(
            floor=Floor(GROUND_FLOOR_NUMBER),
            direction=Direction.UP,
            passengers=(),
        )


def test_elevator_call_rejects_more_passengers_than_capacity() -> None:
    passengers = tuple(
        _upward_passenger(f"passenger-{index}")
        for index in range(ELEVATOR_CAPACITY + 1)
    )

    with pytest.raises(ValueError, match="Quantidade de passageiros inválida"):
        ElevatorCall(
            floor=Floor(GROUND_FLOOR_NUMBER),
            direction=Direction.UP,
            passengers=passengers,
        )


def test_elevator_call_rejects_passenger_from_another_floor() -> None:
    with pytest.raises(ValueError, match="Origem do passageiro incompatível"):
        ElevatorCall(
            floor=Floor(5),
            direction=Direction.UP,
            passengers=(_upward_passenger(),),
        )


def test_elevator_call_rejects_passenger_with_another_direction() -> None:
    with pytest.raises(ValueError, match="Direção do passageiro incompatível"):
        ElevatorCall(
            floor=Floor(GROUND_FLOOR_NUMBER),
            direction=Direction.DOWN,
            passengers=(_upward_passenger(),),
        )


def test_service_round_accepts_one_upward_and_one_downward_call() -> None:
    upward_call, downward_call = _valid_calls()

    service_round = ServiceRound(
        upward_call=upward_call,
        downward_call=downward_call,
    )

    assert service_round.upward_call is upward_call
    assert service_round.downward_call is downward_call


def test_service_round_rejects_swapped_calls() -> None:
    upward_call, downward_call = _valid_calls()

    with pytest.raises(ValueError, match="Chamada de subida inválida"):
        ServiceRound(
            upward_call=downward_call,
            downward_call=upward_call,
        )


def test_service_round_rejects_upward_call_as_downward_call() -> None:
    upward_call, _ = _valid_calls()

    with pytest.raises(ValueError, match="Chamada de descida inválida"):
        ServiceRound(
            upward_call=upward_call,
            downward_call=upward_call,
        )


def test_elevator_event_accepts_passengers_for_entry_and_exit() -> None:
    passenger = _upward_passenger()

    entered_event = ElevatorEvent(
        elapsed_seconds=3,
        floor=passenger.origin,
        direction=Direction.UP,
        kind=EventKind.PASSENGERS_ENTERED,
        passengers=(passenger,),
    )
    exited_event = ElevatorEvent(
        elapsed_seconds=8,
        floor=passenger.destination,
        direction=Direction.UP,
        kind=EventKind.PASSENGERS_EXITED,
        passengers=(passenger,),
    )

    assert entered_event.passengers == (passenger,)
    assert exited_event.passengers == (passenger,)


def test_elevator_event_rejects_passengers_for_other_event_kinds() -> None:
    passenger = _upward_passenger()

    with pytest.raises(ValueError, match="Passageiros incompatíveis"):
        ElevatorEvent(
            elapsed_seconds=1,
            floor=Floor(1),
            direction=Direction.UP,
            kind=EventKind.FLOOR_PASSED,
            passengers=(passenger,),
        )


def test_models_are_immutable() -> None:
    passenger = _upward_passenger()
    upward_call, downward_call = _valid_calls()
    service_round = ServiceRound(upward_call, downward_call)
    event = ElevatorEvent(
        elapsed_seconds=0,
        floor=Floor(GROUND_FLOOR_NUMBER),
        direction=Direction.IDLE,
        kind=EventKind.IDLE,
    )
    snapshot = ElevatorSnapshot(
        current_floor=Floor(GROUND_FLOOR_NUMBER),
        direction=Direction.IDLE,
        cabin=(),
        upward_waiting=(),
        downward_waiting=(),
        elapsed_seconds=0,
        is_idle=True,
    )

    for instance, attribute, value in (
        (passenger, "name", "Outro nome"),
        (upward_call, "passengers", ()),
        (service_round, "upward_call", downward_call),
        (event, "elapsed_seconds", 1),
        (snapshot, "is_idle", False),
    ):
        with pytest.raises(FrozenInstanceError):
            setattr(instance, attribute, value)
