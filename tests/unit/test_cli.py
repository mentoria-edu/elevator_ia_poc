"""Testes unitários da apresentação da CLI do elevador."""

import runpy
from io import StringIO
from unittest.mock import Mock, call, patch

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


def make_snapshot(
    elapsed_seconds: int,
    floor_number: int,
    *,
    upward_waiting: tuple[Mock, ...] = (),
    downward_waiting: tuple[Mock, ...] = (),
) -> Mock:
    """Cria um snapshot com os dados usados no resumo."""
    return Mock(
        elapsed_seconds=elapsed_seconds,
        current_floor=Mock(number=floor_number),
        upward_waiting=upward_waiting,
        downward_waiting=downward_waiting,
    )


def test_demo_executes_one_round_by_default() -> None:
    service_round = make_service_round()
    event = make_event("arrival")
    generator = Mock()
    generator.generate_round.return_value = service_round
    elevator = Mock()
    elevator.run_until_idle.return_value = (event,)
    elevator.snapshot.side_effect = (
        make_snapshot(0, 0),
        make_snapshot(7, 12),
    )
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
        "Chamada de descida: Andar 12 | DESCENDO | Passageiros: Maria Alves",
        "[00:03] Andar 02 | SUBINDO | Chegada",
        "Resumo: Andar final 12 | Tempo 00:07 | Atendidos 3 | "
        "Filas: subida 0, descida 0",
    ]


@pytest.mark.parametrize("rounds", ["0", "-1", "texto"])
def test_demo_rejects_invalid_round_count(rounds: str) -> None:
    with pytest.raises(SystemExit) as error:
        main(["demo", "--rounds", rounds], generator=Mock(), output=StringIO())

    assert error.value.code == 2


def test_demo_executes_three_rounds_on_the_same_elevator() -> None:
    rounds = (
        make_service_round(),
        make_service_round(),
        make_service_round(),
    )
    events = tuple(
        make_event("idle", elapsed_seconds=index) for index in range(3)
    )
    generator = Mock()
    generator.generate_round.side_effect = rounds
    elevator = Mock()
    elevator.run_until_idle.side_effect = (
        (events[0],),
        (events[1],),
        (events[2],),
    )
    elevator.snapshot.side_effect = (
        make_snapshot(0, 0),
        make_snapshot(10, 12),
        make_snapshot(10, 12),
        make_snapshot(18, 0),
        make_snapshot(18, 0),
        make_snapshot(31, 12),
    )
    output = StringIO()

    with patch(
        "elevator_vibe_code.cli._create_elevator",
        return_value=elevator,
    ) as create_elevator:
        result = main(
            ["demo", "--rounds", "3"], generator=generator, output=output
        )

    assert result == 0
    create_elevator.assert_called_once_with()
    assert generator.generate_round.call_count == 3
    elevator.assert_has_calls([
        call.snapshot(),
        call.start_round(rounds[0]),
        call.run_until_idle(),
        call.snapshot(),
        call.snapshot(),
        call.start_round(rounds[1]),
        call.run_until_idle(),
        call.snapshot(),
        call.snapshot(),
        call.start_round(rounds[2]),
        call.run_until_idle(),
        call.snapshot(),
    ])
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
    generator = Mock()
    generator.generate_round.return_value = make_service_round()
    elevator = Mock()
    elevator.run_until_idle.return_value = ()
    elevator.snapshot.side_effect = (
        make_snapshot(0, 0),
        make_snapshot(4, 12),
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


def test_package_entry_point_delegates_without_name_guard() -> None:
    with (
        patch("elevator_vibe_code.cli.main", return_value=7) as mocked_main,
        pytest.raises(SystemExit) as error,
    ):
        runpy.run_module("elevator_vibe_code.__main__")

    mocked_main.assert_called_once_with()
    assert error.value.code == 7
