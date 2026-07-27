"""Interface de linha de comando para acompanhar o elevador."""

# mypy: disable-error-code="import-not-found"

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from elevator_vibe_code.models import ElevatorEvent

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
