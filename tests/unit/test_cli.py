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
    ElevatorEvent,
    ElevatorSnapshot,
    EventKind,
    Floor,
    Passenger,
    ServicePhase,
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
    origin = 0 if direction is Direction.UP else floor_number
    destination = floor_number if direction is Direction.UP else 0
    passengers = tuple(
        make_passenger(f"event-{index}", name, origin, destination)
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

    assert format_event(event) == "[02:05] Andar 17 | DESCENDO | Passando"


def make_service_phases() -> tuple[ServicePhase, ServicePhase]:
    """Cria duas fases reais e determinísticas para a CLI."""
    upward_phase = ServicePhase(
        direction=Direction.UP,
        requests=(
            make_passenger("up-1", "Ana Souza", 0, 4),
            make_passenger("up-2", "Carlos Lima", 0, 8),
        ),
    )
    downward_phase = ServicePhase(
        direction=Direction.DOWN,
        requests=(
            make_passenger("down-1", "Maria Alves", 12, 0),
            make_passenger("down-2", "João Silva", 5, 0),
        ),
    )
    return upward_phase, downward_phase


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


class FakePhaseGenerator:
    """Entrega fases configuradas e registra a ordem de geração."""

    def __init__(
        self,
        upward_phases: tuple[ServicePhase, ...],
        downward_phases: tuple[ServicePhase, ...],
        actions: list[str] | None = None,
    ) -> None:
        self._upward_phases: Iterator[ServicePhase] = iter(upward_phases)
        self._downward_phases: Iterator[ServicePhase] = iter(downward_phases)
        self.actions = actions if actions is not None else []
        self.upward_count = 0
        self.downward_count = 0

    def generate_upward_phase(self) -> ServicePhase:
        """Retorna a próxima subida configurada."""
        self.actions.append("generate_upward_phase")
        self.upward_count += 1
        return next(self._upward_phases)

    def generate_downward_phase(self) -> ServicePhase:
        """Retorna a próxima descida configurada."""
        self.actions.append("generate_downward_phase")
        self.downward_count += 1
        return next(self._downward_phases)


class FakeElevator:
    """Registra a orquestração da CLI sem reproduzir regras do motor."""

    def __init__(
        self,
        snapshots: tuple[ElevatorSnapshot, ...],
        event_batches: tuple[tuple[ElevatorEvent, ...], ...],
        actions: list[str] | None = None,
    ) -> None:
        self._snapshots: Iterator[ElevatorSnapshot] = iter(snapshots)
        self._event_batches: Iterator[tuple[ElevatorEvent, ...]] = iter(
            event_batches
        )
        self.actions = actions if actions is not None else []
        self.started_phases: list[ServicePhase] = []
        self.step_count = 0

    def snapshot(self) -> ElevatorSnapshot:
        """Retorna o próximo snapshot configurado."""
        self.actions.append("snapshot")
        return next(self._snapshots)

    def start_phase(self, phase: ServicePhase) -> None:
        """Registra a fase recebida."""
        self.actions.append(f"start_{phase.direction.name.lower()}_phase")
        self.started_phases.append(phase)

    def step(self) -> tuple[ElevatorEvent, ...]:
        """Retorna o próximo lote de eventos configurado."""
        self.step_count += 1
        self.actions.append(f"step_{self.step_count}")
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


def make_one_step_elevator(
    actions: list[str] | None = None,
) -> FakeElevator:
    """Cria um elevador fake com um passo terminal por fase."""
    upward_event = make_event(EventKind.ARRIVAL)
    downward_event = make_event(
        EventKind.ARRIVAL,
        elapsed_seconds=20,
        floor_number=12,
        direction=Direction.DOWN,
    )
    return FakeElevator(
        (
            make_snapshot(0, 0),
            make_snapshot(8, 8),
            make_snapshot(20, 0),
        ),
        ((upward_event,), (downward_event,)),
        actions,
    )


def make_delayed_elevator() -> FakeElevator:
    """Cria uma subida de dois passos e uma descida terminal."""
    first_event = make_event(EventKind.ARRIVAL)
    upward_idle = make_event(
        EventKind.IDLE,
        elapsed_seconds=8,
        floor_number=8,
        direction=Direction.IDLE,
    )
    downward_idle = make_event(
        EventKind.IDLE,
        elapsed_seconds=15,
        floor_number=0,
        direction=Direction.IDLE,
    )
    return FakeElevator(
        (
            make_snapshot(0, 0),
            make_snapshot(3, 2, is_idle=False),
            make_snapshot(8, 8),
            make_snapshot(15, 0),
        ),
        ((first_event,), (upward_idle,), (downward_idle,)),
    )


def test_demo_executes_two_sequential_phases_by_default() -> None:
    upward_phase, downward_phase = make_service_phases()
    actions: list[str] = []
    generator = FakePhaseGenerator(
        (upward_phase,),
        (downward_phase,),
        actions,
    )
    elevator = make_one_step_elevator(actions)
    output = StringIO()

    with patch(
        "elevator_vibe_code.cli._create_elevator",
        return_value=elevator,
    ) as create_elevator:
        result = main(["demo"], generator=generator, output=output)

    assert result == 0
    create_elevator.assert_called_once_with()
    assert elevator.started_phases == [upward_phase, downward_phase]
    assert actions == [
        "generate_upward_phase",
        "snapshot",
        "start_up_phase",
        "step_1",
        "snapshot",
        "generate_downward_phase",
        "start_down_phase",
        "step_2",
        "snapshot",
    ]
    assert output.getvalue().splitlines() == [
        "Rodada 1",
        "Subida:",
        "- Ana Souza | chamada no andar 00 | destino 04",
        "- Carlos Lima | chamada no andar 00 | destino 08",
        "[00:03] Andar 02 | SUBINDO | Chegada",
        "Descida:",
        "- Maria Alves | chamada no andar 12 | destino 00",
        "- João Silva | chamada no andar 05 | destino 00",
        "[00:20] Andar 12 | DESCENDO | Chegada",
        "Resumo: Andar final 00 | Tempo 00:20 | Atendidos 4 | "
        "Filas: subida 0, descida 0",
    ]


def test_downward_generation_and_list_follow_last_upward_exit() -> None:
    upward_phase, downward_phase = make_service_phases()
    actions: list[str] = []
    generator = FakePhaseGenerator(
        (upward_phase,),
        (downward_phase,),
        actions,
    )
    upward_exit = make_event(
        EventKind.PASSENGERS_EXITED,
        elapsed_seconds=8,
        floor_number=8,
        passenger_names=("Ana Souza",),
    )
    downward_arrival = make_event(
        EventKind.ARRIVAL,
        elapsed_seconds=9,
        floor_number=7,
        direction=Direction.DOWN,
    )
    elevator = FakeElevator(
        (
            make_snapshot(0, 0),
            make_snapshot(8, 8),
            make_snapshot(9, 7),
        ),
        ((upward_exit,), (downward_arrival,)),
        actions,
    )
    output = StringIO()

    with patch(
        "elevator_vibe_code.cli._create_elevator", return_value=elevator
    ):
        main(["demo"], generator=generator, output=output)

    assert actions.index("generate_downward_phase") > actions.index("step_1")
    lines = output.getvalue().splitlines()
    exit_index = lines.index("[00:08] Andar 08 | SUBINDO | Saíram: Ana Souza")
    downward_list_index = lines.index("Descida:")
    first_downward_event_index = lines.index(
        "[00:09] Andar 07 | DESCENDO | Chegada"
    )
    assert exit_index < downward_list_index < first_downward_event_index
    assert "Ana Souza" not in lines[downward_list_index + 1]


def test_demo_waits_default_delay_only_between_steps_after_output() -> None:
    upward_phase, downward_phase = make_service_phases()
    generator = FakePhaseGenerator((upward_phase,), (downward_phase,))
    elevator = make_delayed_elevator()
    output = StringIO()
    sleeper = RecordingSleeper(output)

    with patch(
        "elevator_vibe_code.cli._create_elevator", return_value=elevator
    ):
        result = main(
            ["demo"],
            generator=generator,
            output=output,
            sleeper=sleeper,
        )

    assert result == 0
    assert sleeper.delays == [2.0]
    assert (
        "[00:03] Andar 02 | SUBINDO | Chegada" in sleeper.output_snapshots[0]
    )
    assert "Descida:" not in sleeper.output_snapshots[0]


def test_demo_accepts_decimal_step_delay() -> None:
    upward_phase, downward_phase = make_service_phases()
    elevator = make_delayed_elevator()
    output = StringIO()
    sleeper = RecordingSleeper(output)

    with patch(
        "elevator_vibe_code.cli._create_elevator", return_value=elevator
    ):
        result = main(
            ["demo", "--step-delay", "0.5"],
            generator=FakePhaseGenerator((upward_phase,), (downward_phase,)),
            output=output,
            sleeper=sleeper,
        )

    assert result == 0
    assert sleeper.delays == [0.5]


def test_demo_disables_wait_when_step_delay_is_zero() -> None:
    upward_phase, downward_phase = make_service_phases()
    elevator = make_delayed_elevator()
    output = StringIO()
    sleeper = RecordingSleeper(output)

    with patch(
        "elevator_vibe_code.cli._create_elevator", return_value=elevator
    ):
        result = main(
            ["demo", "--step-delay", "0"],
            generator=FakePhaseGenerator((upward_phase,), (downward_phase,)),
            output=output,
            sleeper=sleeper,
        )

    assert result == 0
    assert sleeper.delays == []
    assert elevator.step_count == 3


@pytest.mark.parametrize("step_delay", ["-0.1", "nan", "inf", "-inf", "texto"])
def test_demo_rejects_invalid_step_delay(step_delay: str) -> None:
    with pytest.raises(SystemExit) as error:
        main(
            ["demo", "--step-delay", step_delay],
            generator=FakePhaseGenerator((), ()),
            output=StringIO(),
        )

    assert error.value.code == 2


def test_demo_rejects_step_delay_with_underscore() -> None:
    with pytest.raises(SystemExit) as error:
        main(
            ["demo", "--step_delay", "2"],
            generator=FakePhaseGenerator((), ()),
            output=StringIO(),
        )

    assert error.value.code == 2


@pytest.mark.parametrize("rounds", ["0", "-1", "texto"])
def test_demo_rejects_invalid_round_count(rounds: str) -> None:
    with pytest.raises(SystemExit) as error:
        main(
            ["demo", "--rounds", rounds],
            generator=FakePhaseGenerator((), ()),
            output=StringIO(),
        )

    assert error.value.code == 2


def test_demo_executes_three_rounds_on_the_same_elevator() -> None:
    upward_phase, downward_phase = make_service_phases()
    generator = FakePhaseGenerator(
        (upward_phase, upward_phase, upward_phase),
        (downward_phase, downward_phase, downward_phase),
    )
    terminal_events = tuple(
        (make_event(EventKind.IDLE, elapsed_seconds=index),)
        for index in range(6)
    )
    elevator = FakeElevator(
        (
            make_snapshot(0, 0),
            make_snapshot(5, 8),
            make_snapshot(10, 0),
            make_snapshot(10, 0),
            make_snapshot(14, 8),
            make_snapshot(18, 0),
            make_snapshot(18, 0),
            make_snapshot(24, 8),
            make_snapshot(31, 0),
        ),
        terminal_events,
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
    assert generator.upward_count == 3
    assert generator.downward_count == 3
    lines = output.getvalue().splitlines()
    assert [line for line in lines if line.startswith("Rodada ")] == [
        "Rodada 1",
        "Rodada 2",
        "Rodada 3",
    ]
    summaries = [line for line in lines if line.startswith("Resumo: ")]
    assert summaries == [
        "Resumo: Andar final 00 | Tempo 00:10 | Atendidos 4 | "
        "Filas: subida 0, descida 0",
        "Resumo: Andar final 00 | Tempo 00:08 | Atendidos 4 | "
        "Filas: subida 0, descida 0",
        "Resumo: Andar final 00 | Tempo 00:13 | Atendidos 4 | "
        "Filas: subida 0, descida 0",
    ]


def test_demo_uses_default_generator_factory() -> None:
    upward_phase, downward_phase = make_service_phases()
    generator = FakePhaseGenerator((upward_phase,), (downward_phase,))
    elevator = make_one_step_elevator()

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
        "elevator_vibe_code.cli._create_elevator", return_value=elevator
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
    assert lines.count("Subida:") == 2
    assert lines.count("Descida:") == 2
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
