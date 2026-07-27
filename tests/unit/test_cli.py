"""Testes unitários da apresentação da CLI do elevador."""

from io import StringIO
from unittest.mock import Mock, patch

import pytest

from elevator_vibe_code.cli import format_event, main


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

def make_call(
    floor_number: int,
    direction: str,
    passenger_names: tuple[str, ...],
) -> Mock:
    """Cria um mock de chamada exibível pela CLI."""
    return Mock(
        floor=Mock(number=floor_number),
        direction=Mock(value=direction),
        passengers=tuple(make_passenger(name) for name in passenger_names),
    )


def make_service_round() -> Mock:
    """Cria uma rodada com chamadas determinísticas."""
    return Mock(
        upward_call=make_call(0, "SUBINDO", ("Ana Souza", "Carlos Lima")),
        downward_call=make_call(12, "DESCENDO", ("Maria Alves",)),
    )


def test_demo_executes_one_round_by_default() -> None:
    service_round = make_service_round()
    event = make_event("arrival")
    generator = Mock()
    generator.generate_round.return_value = service_round
    elevator = Mock()
    elevator.run_until_idle.return_value = (event,)
    output = StringIO()

    with patch(
        "elevator_vibe_code.cli._create_elevator",
        return_value=elevator,
    ) as create_elevator:
        result = main(["demo"], generator=generator, output=output)

    assert result == 0
    create_elevator.assert_called_once_with()
    generator.generate_round.assert_called_once_with()
    elevator.start_round.assert_called_once_with(service_round)
    elevator.run_until_idle.assert_called_once_with()
    assert output.getvalue().splitlines() == [
        "Rodada 1",
        "Chamada de subida: Andar 00 | SUBINDO | "
        "Passageiros: Ana Souza, Carlos Lima",
        "Chamada de descida: Andar 12 | DESCENDO | "
        "Passageiros: Maria Alves",
        "[00:03] Andar 02 | SUBINDO | Chegada",
    ]


@pytest.mark.parametrize("rounds", ["0", "-1", "texto"])
def test_demo_rejects_invalid_round_count(rounds: str) -> None:
    with pytest.raises(SystemExit) as error:
        main(["demo", "--rounds", rounds], generator=Mock(), output=StringIO())

    assert error.value.code == 2
