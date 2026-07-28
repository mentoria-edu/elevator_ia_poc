"""Testes dos modelos imutáveis do elevador."""

from dataclasses import FrozenInstanceError

import pytest

from elevator_vibe_code.models import (
    ELEVATOR_CAPACITY,
    GROUND_FLOOR_NUMBER,
    TOP_FLOOR_NUMBER,
    Direction,
    ElevatorEvent,
    ElevatorSnapshot,
    EventKind,
    Floor,
    Passenger,
    ServicePhase,
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
    assert _upward_passenger().direction is Direction.UP
    assert _downward_passenger().direction is Direction.DOWN


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


def test_service_phase_preserves_individual_requests_in_fifo_order() -> None:
    first = _upward_passenger("first", destination=8)
    second = _upward_passenger("second", destination=8)

    phase = ServicePhase(direction=Direction.UP, requests=(first, second))

    assert phase.requests == (first, second)
    assert first.destination == second.destination
    assert first.passenger_id != second.passenger_id


@pytest.mark.parametrize("request_count", [0, ELEVATOR_CAPACITY + 1])
def test_service_phase_rejects_invalid_request_count(
    request_count: int,
) -> None:
    requests = tuple(
        _upward_passenger(f"passenger-{index}")
        for index in range(request_count)
    )

    with pytest.raises(ValueError, match="Quantidade de solicitações"):
        ServicePhase(direction=Direction.UP, requests=requests)


def test_service_phase_rejects_idle_direction() -> None:
    with pytest.raises(ValueError, match="Direção de fase inválida"):
        ServicePhase(
            direction=Direction.IDLE,
            requests=(_upward_passenger(),),
        )


def test_service_phase_rejects_passenger_with_another_direction() -> None:
    with pytest.raises(ValueError, match="incompatível com a fase"):
        ServicePhase(
            direction=Direction.UP,
            requests=(_downward_passenger(),),
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
    phase = ServicePhase(Direction.UP, (passenger,))
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
        (phase, "requests", ()),
        (event, "elapsed_seconds", 1),
        (snapshot, "is_idle", False),
    ):
        with pytest.raises(FrozenInstanceError):
            setattr(instance, attribute, value)
