"""Testes da interface de linha de comando."""

from pathlib import Path

import pytest

from tests.garbage_collector.helpers import (
    FakeRepositoryPathProvider,
    fixed_now,
    write_valid_configuration,
)
from tools.garbage_collector.cli import run
from tools.garbage_collector.models import RepositoryPaths
from tools.garbage_collector.scan import RepositoryAccessError


class FailingRepositoryPathProvider:
    """Simula uma raiz que o Git não consegue enumerar."""

    def list_paths(self, project_root: Path) -> RepositoryPaths:
        """Falha de forma observável sem executar subprocesso."""
        raise RepositoryAccessError(
            f"Git não conseguiu enumerar {project_root}"
        )


@pytest.mark.parametrize(
    ("command", "expected"),
    [
        ("scan", (False, False, False)),
        ("inventory", (True, True, False)),
        ("report", (False, False, True)),
        ("check", (True, True, True)),
    ],
)
def test_subcommands_write_only_their_allowed_outputs(
    tmp_path: Path,
    command: str,
    expected: tuple[bool, bool, bool],
) -> None:
    write_valid_configuration(tmp_path)
    marker = tmp_path / "marker.txt"
    marker.write_text("unchanged", encoding="utf-8")
    provider = FakeRepositoryPathProvider(
        visible=("artifact.tmp",),
        tracked=("artifact.tmp",),
    )

    exit_code = run(
        (command, "--project-root", str(tmp_path)),
        path_provider=provider,
        now=fixed_now,
    )

    inventory = tmp_path / "docs/garbage-collector/inventory/inventory.yml"
    history = (
        tmp_path
        / "docs/garbage-collector/inventory/history"
        / "2026-07-25T123000Z.yml"
    )
    report = tmp_path / "docs/garbage-collector/reports/2026-07-25-scan.md"
    assert exit_code == 0
    assert (inventory.exists(), history.exists(), report.exists()) == expected
    assert marker.read_text(encoding="utf-8") == "unchanged"


@pytest.mark.parametrize(
    ("threshold", "expected_code"),
    [("warning", 1), ("error", 0)],
)
def test_fail_on_uses_requested_threshold(
    tmp_path: Path, threshold: str, expected_code: int
) -> None:
    write_valid_configuration(tmp_path)
    provider = FakeRepositoryPathProvider(
        visible=("artifact.tmp",),
        tracked=("artifact.tmp",),
    )

    exit_code = run(
        (
            "scan",
            "--project-root",
            str(tmp_path),
            "--fail-on",
            threshold,
        ),
        path_provider=provider,
        now=fixed_now,
    )

    assert exit_code == expected_code


def test_fail_on_error_returns_one_for_error_candidate(
    tmp_path: Path,
) -> None:
    write_valid_configuration(
        tmp_path,
        rules=(
            "version: 1\nrules:\n"
            "  - id: error-rule\n"
            "    description: Erro observável\n"
            "    patterns: ['*.tmp']\n"
            "    severity: error\n"
            "    action: review\n"
        ),
    )

    exit_code = run(
        (
            "scan",
            "--project-root",
            str(tmp_path),
            "--fail-on",
            "error",
        ),
        path_provider=FakeRepositoryPathProvider(
            visible=("artifact.tmp",),
        ),
        now=fixed_now,
    )

    assert exit_code == 1


def test_invalid_configuration_returns_two_and_report_writes_error(
    tmp_path: Path,
) -> None:
    write_valid_configuration(tmp_path, rules="version: 1\nrules: [")

    exit_code = run(
        ("report", "--project-root", str(tmp_path)),
        path_provider=FakeRepositoryPathProvider(),
        now=fixed_now,
    )

    report = tmp_path / "docs/garbage-collector/reports/2026-07-25-scan.md"
    assert exit_code == 2
    assert "Erros de configuração" in report.read_text(encoding="utf-8")


def test_unsafe_configuration_does_not_write_report(tmp_path: Path) -> None:
    write_valid_configuration(tmp_path)

    exit_code = run(
        (
            "report",
            "--project-root",
            str(tmp_path),
            "--rules-file",
            "../outside.yml",
        ),
        path_provider=FakeRepositoryPathProvider(),
        now=fixed_now,
    )

    assert exit_code == 2
    assert not (
        tmp_path / "docs/garbage-collector/reports/2026-07-25-scan.md"
    ).exists()


def test_invalid_project_root_returns_two(tmp_path: Path) -> None:
    exit_code = run(
        ("scan", "--project-root", str(tmp_path / "missing")),
        path_provider=FakeRepositoryPathProvider(),
        now=fixed_now,
    )

    assert exit_code == 2


def test_repository_access_error_returns_two(tmp_path: Path) -> None:
    write_valid_configuration(tmp_path)

    exit_code = run(
        ("scan", "--project-root", str(tmp_path)),
        path_provider=FailingRepositoryPathProvider(),
        now=fixed_now,
    )

    assert exit_code == 2


def test_history_collision_returns_three(tmp_path: Path) -> None:
    write_valid_configuration(tmp_path)
    provider = FakeRepositoryPathProvider()
    arguments = ("inventory", "--project-root", str(tmp_path))
    assert run(arguments, path_provider=provider, now=fixed_now) == 0

    exit_code = run(
        arguments,
        path_provider=provider,
        now=fixed_now,
    )

    assert exit_code == 3
