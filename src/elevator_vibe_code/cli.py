"""Interface de linha de comando para acompanhar o elevador."""

# mypy: disable-error-code="import-not-found"

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from typing import TYPE_CHECKING, Protocol, TextIO

if TYPE_CHECKING:
    from elevator_vibe_code.generation import RoundGenerator
    from elevator_vibe_code.models import (
        ElevatorEvent,
        ElevatorSnapshot,
        ServiceRound,
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

    def start_round(self, service_round: ServiceRound) -> None:
        """Inicia uma rodada de atendimento."""

    def run_until_idle(self) -> tuple[ElevatorEvent, ...]:
        """Executa a rodada até o elevador ficar ocioso."""

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


def _create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="elevator_vibe_code")
    commands = parser.add_subparsers(dest="command", required=True)
    demo_parser = commands.add_parser("demo")
    demo_parser.add_argument("--rounds", type=_positive_int, default=1)
    return parser


def _create_generator() -> RoundGenerator:
    from elevator_vibe_code.generation import FakerPassengerGenerator

    generator: RoundGenerator = FakerPassengerGenerator()
    return generator


def _create_elevator() -> _Elevator:
    from elevator_vibe_code.elevator import Elevator

    elevator: _Elevator = Elevator()
    return elevator


def _format_call(label: str, elevator_call: object) -> str:
    floor = getattr(elevator_call, "floor")
    direction = getattr(elevator_call, "direction")
    passengers = getattr(elevator_call, "passengers")
    names = ", ".join(passenger.name for passenger in passengers)
    return (
        f"{label}: Andar {floor.number:02d} | {direction.value} | "
        f"Passageiros: {names}"
    )


def main(
    argv: Sequence[str] | None = None,
    *,
    generator: RoundGenerator | None = None,
    output: TextIO | None = None,
) -> int:
    """Executa a demonstração solicitada pela linha de comando."""
    arguments = _create_parser().parse_args(argv)
    round_generator = generator or _create_generator()
    elevator = _create_elevator()
    stream = output or sys.stdout

    for round_number in range(1, arguments.rounds + 1):
        service_round = round_generator.generate_round()
        print(f"Rodada {round_number}", file=stream)
        print(
            _format_call("Chamada de subida", service_round.upward_call),
            file=stream,
        )
        print(
            _format_call("Chamada de descida", service_round.downward_call),
            file=stream,
        )
        elevator.start_round(service_round)
        for event in elevator.run_until_idle():
            print(format_event(event), file=stream)

    return 0
