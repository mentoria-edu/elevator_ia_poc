"""Testes unitários e de composição da CLI do elevador."""

import runpy
from collections.abc import Iterator
from io import StringIO
from unittest.mock import patch

import pytest
from faker import Faker

from elevator_vibe_code.cli import format_event, main
from elevator_vibe_code.elevator import Elevator
from elevator_vibe_code.generation import FakerPassengerGenerator
from elevator_vibe_code.models import (
    Direction,
    ElevatorCall,
    ElevatorEvent,
    ElevatorSnapshot,
    EventKind,
    Floor,
    Passenger,
    ServiceRound,
)


def make_passenger(
    passenger_id: str,
    name: str,
    origin: int,
    destination: int,
) -> Passenger:
    """Cria um passageiro válido e identificável."""
    direction = Direction.UP if destination > origin else Direction.DOWN
    return Passenger(
        passenger_id=passenger_id,
        name=name,
        origin=Floor(origin),
        destination=Floor(destination),
        direction=direction,
    )


def make_event(
    kind: EventKind,
    *,
    elapsed_seconds: int = 3,
    floor_number: int = 2,
    direction: Direction = Direction.UP,
    passenger_names: tuple[str, ...] = (),
) -> ElevatorEvent:
    """Cria um evento real com os dados observados pela CLI."""
    passengers = tuple(
        make_passenger(f"event-{index}", name, 0, 2)
        for index, name in enumerate(passenger_names)
    )
    return ElevatorEvent(
        elapsed_seconds=elapsed_seconds,
        floor=Floor(floor_number),
        direction=direction,
        kind=kind,
        passengers=passengers,
    )


@pytest.mark.parametrize(
    ("kind", "description"),
    [
        (EventKind.FLOOR_PASSED, "Passando"),
        (EventKind.ARRIVAL, "Chegada"),
        (EventKind.DOOR_OPENING, "Porta abrindo"),
        (EventKind.DOOR_CLOSING, "Porta fechando"),
        (EventKind.DIRECTION_CHANGED, "Direção alterada"),
        (EventKind.IDLE, "Elevador parado"),
    ],
)
def test_format_event_describes_operational_event(
    kind: EventKind,
    description: str,
) -> None:
    event = make_event(kind)

    result = format_event(event)

    assert result == f"[00:03] Andar 02 | SUBINDO | {description}"


@pytest.mark.parametrize(
    ("kind", "description"),
    [
        (EventKind.PASSENGERS_EXITED, "Saíram"),
        (EventKind.PASSENGERS_ENTERED, "Entraram"),
    ],
)
def test_format_event_preserves_passenger_order(
    kind: EventKind,
    description: str,
) -> None:
    event = make_event(
        kind,
        passenger_names=("Ana Souza", "Carlos Lima", "Maria Alves"),
    )

    result = format_event(event)

    assert result == (
        f"[00:03] Andar 02 | SUBINDO | {description}: "
        "Ana Souza, Carlos Lima, Maria Alves"
    )


def test_format_event_formats_minutes_floor_and_direction() -> None:
    event = make_event(
        EventKind.FLOOR_PASSED,
        elapsed_seconds=125,
        floor_number=17,
        direction=Direction.DOWN,
    )

    result = format_event(event)

    assert result == "[02:05] Andar 17 | DESCENDO | Passando"


def make_service_round() -> ServiceRound:
    """Cria uma rodada real e determinística para os testes da CLI."""
    upward_passengers = (
        make_passenger("up-1", "Ana Souza", 0, 4),
        make_passenger("up-2", "Carlos Lima", 0, 8),
    )
    downward_passengers = (make_passenger("down-1", "Maria Alves", 12, 0),)
    return ServiceRound(
        upward_call=ElevatorCall(
            floor=Floor(0),
            direction=Direction.UP,
            passengers=upward_passengers,
        ),
        downward_call=ElevatorCall(
            floor=Floor(12),
            direction=Direction.DOWN,
            passengers=downward_passengers,
        ),
    )


def make_snapshot(
    elapsed_seconds: int,
    floor_number: int,
    *,
    upward_waiting: tuple[Passenger, ...] = (),
    downward_waiting: tuple[Passenger, ...] = (),
    is_idle: bool = True,
) -> ElevatorSnapshot:
    """Cria um snapshot real com os dados usados no resumo."""
    return ElevatorSnapshot(
        current_floor=Floor(floor_number),
        direction=Direction.IDLE,
        cabin=(),
        upward_waiting=upward_waiting,
        downward_waiting=downward_waiting,
        elapsed_seconds=elapsed_seconds,
        is_idle=is_idle,
    )


class FakeRoundGenerator:
    """Entrega rodadas configuradas e registra quantas foram solicitadas."""

    def __init__(self, rounds: tuple[ServiceRound, ...]) -> None:
        self._rounds: Iterator[ServiceRound] = iter(rounds)
        self.generate_count = 0

    def generate_round(self) -> ServiceRound:
        """Retorna a próxima rodada configurada."""
        self.generate_count += 1
        return next(self._rounds)


class FakeElevator:
    """Registra a orquestração da CLI sem reproduzir regras do motor."""

    def __init__(
        self,
        snapshots: tuple[ElevatorSnapshot, ...],
        event_batches: tuple[tuple[ElevatorEvent, ...], ...],
    ) -> None:
        self._snapshots: Iterator[ElevatorSnapshot] = iter(snapshots)
        self._event_batches: Iterator[tuple[ElevatorEvent, ...]] = iter(
            event_batches
        )
        self.actions: list[str] = []
        self.started_rounds: list[ServiceRound] = []

    def snapshot(self) -> ElevatorSnapshot:
        """Retorna o próximo snapshot configurado."""
        self.actions.append("snapshot")
        return next(self._snapshots)

    def start_round(self, service_round: ServiceRound) -> None:
        """Registra a rodada recebida."""
        self.actions.append("start_round")
        self.started_rounds.append(service_round)

    def step(self) -> tuple[ElevatorEvent, ...]:
        """Retorna o próximo lote de eventos configurado."""
        self.actions.append("step")
        return next(self._event_batches)


class RecordingSleeper:
    """Registra esperas e a saída disponível quando elas acontecem."""

    def __init__(self, output: StringIO) -> None:
        self._output = output
        self.delays: list[float] = []
        self.output_snapshots: list[str] = []

    def __call__(self, delay: float) -> None:
        """Registra o delay sem aguardar em tempo real."""
        self.delays.append(delay)
        self.output_snapshots.append(self._output.getvalue())


def make_two_step_elevator() -> FakeElevator:
    """Cria um elevador fake com um passo intermediário e um terminal."""
    first_event = make_event(EventKind.ARRIVAL)
    final_event = make_event(
        EventKind.IDLE,
        elapsed_seconds=7,
        floor_number=12,
        direction=Direction.IDLE,
    )
    return FakeElevator(
        (
            make_snapshot(0, 0),
            make_snapshot(3, 2, is_idle=False),
            make_snapshot(7, 12),
        ),
        ((first_event,), (final_event,)),
    )


def test_demo_executes_one_round_by_default() -> None:
    service_round = make_service_round()
    event = make_event(EventKind.ARRIVAL)
    generator = FakeRoundGenerator((service_round,))
    elevator = FakeElevator(
        (make_snapshot(0, 0), make_snapshot(7, 12)),
        ((event,),),
    )
    output = StringIO()

    with patch(
        "elevator_vibe_code.cli._create_elevator",
        return_value=elevator,
    ) as create_elevator:
        result = main(["demo"], generator=generator, output=output)

    assert result == 0
    create_elevator.assert_called_once_with()
    assert generator.generate_count == 1
    assert elevator.started_rounds == [service_round]
    assert elevator.actions == [
        "snapshot",
        "start_round",
        "step",
        "snapshot",
    ]
    assert output.getvalue().splitlines() == [
        "Rodada 1",
        "Chamada de subida: Andar 00 | SUBINDO | "
        "Passageiros: Ana Souza, Carlos Lima",
        "Chamada de descida: Andar 12 | DESCENDO | Passageiros: Maria Alves",
        "[00:03] Andar 02 | SUBINDO | Chegada",
        "Resumo: Andar final 12 | Tempo 00:07 | Atendidos 3 | "
        "Filas: subida 0, descida 0",
    ]


def test_demo_waits_default_delay_only_between_steps_after_output() -> None:
    service_round = make_service_round()
    generator = FakeRoundGenerator((service_round,))
    elevator = make_two_step_elevator()
    output = StringIO()
    sleeper = RecordingSleeper(output)

    with patch(
        "elevator_vibe_code.cli._create_elevator",
        return_value=elevator,
    ):
        result = main(
            ["demo"],
            generator=generator,
            output=output,
            sleeper=sleeper,
        )

    assert result == 0
    assert sleeper.delays == [2.0]
    assert len(sleeper.output_snapshots) == 1
    output_before_delay = sleeper.output_snapshots[0]
    assert "[00:03] Andar 02 | SUBINDO | Chegada" in output_before_delay
    assert (
        "[00:07] Andar 12 | PARADO | Elevador parado"
        not in output_before_delay
    )
    assert elevator.actions == [
        "snapshot",
        "start_round",
        "step",
        "snapshot",
        "step",
        "snapshot",
    ]
    assert output.getvalue().splitlines()[-2:] == [
        "[00:07] Andar 12 | PARADO | Elevador parado",
        "Resumo: Andar final 12 | Tempo 00:07 | Atendidos 3 | "
        "Filas: subida 0, descida 0",
    ]


def test_demo_accepts_decimal_step_delay() -> None:
    service_round = make_service_round()
    generator = FakeRoundGenerator((service_round,))
    elevator = make_two_step_elevator()
    output = StringIO()
    sleeper = RecordingSleeper(output)

    with patch(
        "elevator_vibe_code.cli._create_elevator",
        return_value=elevator,
    ):
        result = main(
            ["demo", "--step-delay", "0.5"],
            generator=generator,
            output=output,
            sleeper=sleeper,
        )

    assert result == 0
    assert sleeper.delays == [0.5]


def test_demo_disables_wait_when_step_delay_is_zero() -> None:
    service_round = make_service_round()
    generator = FakeRoundGenerator((service_round,))
    elevator = make_two_step_elevator()
    output = StringIO()
    sleeper = RecordingSleeper(output)

    with patch(
        "elevator_vibe_code.cli._create_elevator",
        return_value=elevator,
    ):
        result = main(
            ["demo", "--step-delay", "0"],
            generator=generator,
            output=output,
            sleeper=sleeper,
        )

    assert result == 0
    assert sleeper.delays == []
    assert elevator.actions.count("step") == 2


@pytest.mark.parametrize("step_delay", ["-0.1", "nan", "inf", "-inf", "texto"])
def test_demo_rejects_invalid_step_delay(step_delay: str) -> None:
    with pytest.raises(SystemExit) as error:
        main(
            ["demo", "--step-delay", step_delay],
            generator=FakeRoundGenerator(()),
            output=StringIO(),
        )

    assert error.value.code == 2


def test_demo_rejects_step_delay_with_underscore() -> None:
    with pytest.raises(SystemExit) as error:
        main(
            ["demo", "--step_delay", "2"],
            generator=FakeRoundGenerator(()),
            output=StringIO(),
        )

    assert error.value.code == 2


@pytest.mark.parametrize("rounds", ["0", "-1", "texto"])
def test_demo_rejects_invalid_round_count(rounds: str) -> None:
    with pytest.raises(SystemExit) as error:
        main(
            ["demo", "--rounds", rounds],
            generator=FakeRoundGenerator(()),
            output=StringIO(),
        )

    assert error.value.code == 2


def test_demo_executes_three_rounds_on_the_same_elevator() -> None:
    rounds = (
        make_service_round(),
        make_service_round(),
        make_service_round(),
    )
    events = tuple(
        make_event(
            EventKind.IDLE,
            elapsed_seconds=index,
            direction=Direction.IDLE,
        )
        for index in range(3)
    )
    generator = FakeRoundGenerator(rounds)
    elevator = FakeElevator(
        (
            make_snapshot(0, 0),
            make_snapshot(10, 12),
            make_snapshot(10, 12),
            make_snapshot(18, 0),
            make_snapshot(18, 0),
            make_snapshot(31, 12),
        ),
        ((events[0],), (events[1],), (events[2],)),
    )
    output = StringIO()

    with patch(
        "elevator_vibe_code.cli._create_elevator",
        return_value=elevator,
    ) as create_elevator:
        result = main(
            ["demo", "--rounds", "3"],
            generator=generator,
            output=output,
        )

    assert result == 0
    create_elevator.assert_called_once_with()
    assert generator.generate_count == 3
    assert elevator.started_rounds == list(rounds)
    assert elevator.actions == [
        "snapshot",
        "start_round",
        "step",
        "snapshot",
        "snapshot",
        "start_round",
        "step",
        "snapshot",
        "snapshot",
        "start_round",
        "step",
        "snapshot",
    ]
    lines = output.getvalue().splitlines()
    round_headers = [line for line in lines if line.startswith("Rodada ")]
    assert round_headers == ["Rodada 1", "Rodada 2", "Rodada 3"]
    summaries = [line for line in lines if line.startswith("Resumo: ")]
    assert summaries == [
        "Resumo: Andar final 12 | Tempo 00:10 | Atendidos 3 | "
        "Filas: subida 0, descida 0",
        "Resumo: Andar final 00 | Tempo 00:08 | Atendidos 3 | "
        "Filas: subida 0, descida 0",
        "Resumo: Andar final 12 | Tempo 00:13 | Atendidos 3 | "
        "Filas: subida 0, descida 0",
    ]


def test_demo_uses_default_generator_factory() -> None:
    service_round = make_service_round()
    generator = FakeRoundGenerator((service_round,))
    elevator = FakeElevator(
        (make_snapshot(0, 0), make_snapshot(4, 12)),
        ((),),
    )

    with (
        patch(
            "elevator_vibe_code.cli._create_generator",
            return_value=generator,
        ) as create_generator,
        patch(
            "elevator_vibe_code.cli._create_elevator",
            return_value=elevator,
        ),
    ):
        result = main(["demo"], output=StringIO())

    assert result == 0
    create_generator.assert_called_once_with()


def test_demo_composes_seeded_generation_models_engine_and_cli() -> None:
    faker_instance = Faker("pt_BR")
    faker_instance.seed_instance(20260727)
    generator = FakerPassengerGenerator(faker_instance)
    elevator = Elevator()
    output = StringIO()

    with patch(
        "elevator_vibe_code.cli._create_elevator",
        return_value=elevator,
    ):
        result = main(
            ["demo", "--rounds", "2", "--step-delay", "0"],
            generator=generator,
            output=output,
        )

    snapshot = elevator.snapshot()
    lines = output.getvalue().splitlines()
    summaries = [line for line in lines if line.startswith("Resumo: ")]

    assert result == 0
    assert [line for line in lines if line.startswith("Rodada ")] == [
        "Rodada 1",
        "Rodada 2",
    ]
    assert len(summaries) == 2
    assert all(
        summary.endswith("Filas: subida 0, descida 0") for summary in summaries
    )
    assert any(" | Entraram: " in line for line in lines)
    assert any(" | Saíram: " in line for line in lines)
    assert snapshot.is_idle
    assert snapshot.cabin == ()
    assert snapshot.upward_waiting == ()
    assert snapshot.downward_waiting == ()


def test_package_entry_point_delegates_without_name_guard() -> None:
    with (
        patch("elevator_vibe_code.cli.main", return_value=7) as mocked_main,
        pytest.raises(SystemExit) as error,
    ):
        runpy.run_module("elevator_vibe_code.__main__")

    mocked_main.assert_called_once_with()
    assert error.value.code == 7
