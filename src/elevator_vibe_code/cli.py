"""Interface de linha de comando para acompanhar o elevador."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable, Sequence
from math import isfinite
from time import sleep
from typing import TYPE_CHECKING, Protocol, TextIO

if TYPE_CHECKING:
    from elevator_vibe_code.generation import PhaseGenerator
    from elevator_vibe_code.models import (
        ElevatorEvent,
        ElevatorSnapshot,
        ServicePhase,
    )

_EVENT_DESCRIPTIONS = {
    "floor_passed": "Passando",
    "arrival": "Chegada",
    "door_opening": "Porta abrindo",
    "passengers_exited": "Saíram",
    "passengers_entered": "Entraram",
    "door_closing": "Porta fechando",
    "direction_changed": "Direção alterada",
    "idle": "Elevador parado",
}
_PASSENGER_EVENT_KINDS = {"passengers_exited", "passengers_entered"}


class _Elevator(Protocol):
    """Operações do motor consumidas pela CLI."""

    def start_phase(self, phase: ServicePhase) -> None:
        """Inicia uma fase de atendimento."""

    def step(self) -> tuple[ElevatorEvent, ...]:
        """Executa o próximo passo da fase."""

    def snapshot(self) -> ElevatorSnapshot:
        """Retorna o estado observável do elevador."""


def format_event(event: ElevatorEvent) -> str:
    """Formata um evento do elevador como uma linha cronológica."""
    minutes, seconds = divmod(event.elapsed_seconds, 60)
    event_kind = event.kind.value
    description = _EVENT_DESCRIPTIONS[event_kind]
    if event_kind in _PASSENGER_EVENT_KINDS:
        names = ", ".join(passenger.name for passenger in event.passengers)
        description = f"{description}: {names}"

    return (
        f"[{minutes:02d}:{seconds:02d}] "
        f"Andar {event.floor.number:02d} | "
        f"{event.direction.value} | {description}"
    )


def _positive_int(value: str) -> int:
    rounds = int(value)
    if rounds < 1:
        raise argparse.ArgumentTypeError(
            f"quantidade de rodadas inválida: {value}. "
            "Esperado um inteiro positivo."
        )
    return rounds


def _non_negative_float(value: str) -> float:
    try:
        delay = float(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            f"delay entre steps inválido: {value}. "
            "Esperado um número finito maior ou igual a zero."
        ) from error

    if not isfinite(delay) or delay < 0:
        raise argparse.ArgumentTypeError(
            f"delay entre steps inválido: {value}. "
            "Esperado um número finito maior ou igual a zero."
        )
    return delay


def _create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="elevator_vibe_code")
    commands = parser.add_subparsers(dest="command", required=True)
    demo_parser = commands.add_parser("demo")
    demo_parser.add_argument("--rounds", type=_positive_int, default=1)
    demo_parser.add_argument(
        "--step-delay",
        type=_non_negative_float,
        default=2.0,
        metavar="SEGUNDOS",
    )
    return parser


def _create_generator() -> PhaseGenerator:
    from elevator_vibe_code.generation import FakerPassengerGenerator

    generator: PhaseGenerator = FakerPassengerGenerator()
    return generator


def _create_elevator() -> _Elevator:
    from elevator_vibe_code.elevator import Elevator

    elevator: _Elevator = Elevator()
    return elevator


def _format_phase(label: str, phase: ServicePhase) -> str:
    lines = [f"{label}:"]
    lines.extend(
        f"- {request.name} | "
        f"chamada no andar {request.origin.number:02d} | "
        f"destino {request.destination.number:02d}"
        for request in phase.requests
    )
    return "\n".join(lines)


def _format_duration(elapsed_seconds: int) -> str:
    minutes, seconds = divmod(elapsed_seconds, 60)
    return f"{minutes:02d}:{seconds:02d}"


def _format_summary(
    initial_snapshot: ElevatorSnapshot,
    final_snapshot: ElevatorSnapshot,
    attended_count: int,
) -> str:
    duration = (
        final_snapshot.elapsed_seconds - initial_snapshot.elapsed_seconds
    )
    return (
        f"Resumo: Andar final {final_snapshot.current_floor.number:02d} | "
        f"Tempo {_format_duration(duration)} | "
        f"Atendidos {attended_count} | "
        f"Filas: subida {len(final_snapshot.upward_waiting)}, "
        f"descida {len(final_snapshot.downward_waiting)}"
    )


def _run_steps_until_idle(
    elevator: _Elevator,
    *,
    step_delay: float,
    sleeper: Callable[[float], None],
    stream: TextIO,
) -> ElevatorSnapshot:
    while True:
        for event in elevator.step():
            print(format_event(event), file=stream)

        snapshot = elevator.snapshot()
        if snapshot.is_idle:
            return snapshot

        stream.flush()
        if step_delay > 0:
            sleeper(step_delay)


def main(
    argv: Sequence[str] | None = None,
    *,
    generator: PhaseGenerator | None = None,
    output: TextIO | None = None,
    sleeper: Callable[[float], None] = sleep,
) -> int:
    """Executa a demonstração solicitada pela linha de comando."""
    arguments = _create_parser().parse_args(argv)
    phase_generator = (
        generator if generator is not None else _create_generator()
    )
    elevator = _create_elevator()
    stream = output if output is not None else sys.stdout

    for round_number in range(1, arguments.rounds + 1):
        upward_phase = phase_generator.generate_upward_phase()
        print(f"Rodada {round_number}", file=stream)
        print(_format_phase("Subida", upward_phase), file=stream)
        initial_snapshot = elevator.snapshot()
        elevator.start_phase(upward_phase)
        _run_steps_until_idle(
            elevator,
            step_delay=arguments.step_delay,
            sleeper=sleeper,
            stream=stream,
        )

        downward_phase = phase_generator.generate_downward_phase()
        print(_format_phase("Descida", downward_phase), file=stream)
        elevator.start_phase(downward_phase)
        final_snapshot = _run_steps_until_idle(
            elevator,
            step_delay=arguments.step_delay,
            sleeper=sleeper,
            stream=stream,
        )
        attended_count = len(upward_phase.requests) + len(
            downward_phase.requests
        )
        print(
            _format_summary(
                initial_snapshot,
                final_snapshot,
                attended_count,
            ),
            file=stream,
        )

    return 0
