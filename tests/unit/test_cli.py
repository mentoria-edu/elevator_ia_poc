"""Testes unitários da apresentação da CLI do elevador."""

from unittest.mock import Mock

import pytest

from elevator_vibe_code.cli import format_event


def make_passenger(name: str) -> Mock:
    """Cria um mock de passageiro com nome observável."""
    passenger = Mock()
    passenger.name = name
    return passenger


def make_event(
    kind: str,
    *,
    elapsed_seconds: int = 3,
    floor_number: int = 2,
    direction: str = "SUBINDO",
    passenger_names: tuple[str, ...] = (),
) -> Mock:
    """Cria um mock de evento com os atributos consumidos pela CLI."""
    return Mock(
        elapsed_seconds=elapsed_seconds,
        floor=Mock(number=floor_number),
        direction=Mock(value=direction),
        kind=Mock(value=kind),
        passengers=tuple(make_passenger(name) for name in passenger_names),
    )


@pytest.mark.parametrize(
    ("kind", "description"),
    [
        ("floor_passed", "Passando"),
        ("arrival", "Chegada"),
        ("door_opening", "Porta abrindo"),
        ("door_closing", "Porta fechando"),
        ("direction_changed", "Direção alterada"),
        ("idle", "Elevador parado"),
    ],
)
def test_format_event_describes_operational_event(
    kind: str,
    description: str,
) -> None:
    event = make_event(kind)

    result = format_event(event)

    assert result == f"[00:03] Andar 02 | SUBINDO | {description}"


@pytest.mark.parametrize(
    ("kind", "description"),
    [
        ("passengers_exited", "Saíram"),
        ("passengers_entered", "Entraram"),
    ],
)
def test_format_event_preserves_passenger_order(
    kind: str,
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
        "floor_passed",
        elapsed_seconds=125,
        floor_number=17,
        direction="DESCENDO",
    )

    result = format_event(event)

    assert result == "[02:05] Andar 17 | DESCENDO | Passando"
