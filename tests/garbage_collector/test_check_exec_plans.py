"""Testes do validador de ExecPlans."""

from pathlib import Path

from tools.validators.check_exec_plans import (
    find_missing_directories,
    find_plan_issues,
)


def test_find_missing_directories_returns_empty_tuple_when_structure_exists(
    tmp_path: Path,
) -> None:
    (tmp_path / "docs/exec-plans/active").mkdir(parents=True)
    (tmp_path / "docs/exec-plans/completed").mkdir(parents=True)

    assert find_missing_directories(tmp_path) == ()


def test_find_missing_directories_lists_missing_directory(
    tmp_path: Path,
) -> None:
    (tmp_path / "docs/exec-plans/active").mkdir(parents=True)

    assert find_missing_directories(tmp_path) == (
        Path("docs/exec-plans/completed"),
    )


def test_find_plan_issues_reports_missing_required_section(
    tmp_path: Path,
) -> None:
    active_directory = tmp_path / "docs/exec-plans/active"
    active_directory.mkdir(parents=True)
    (tmp_path / "docs/exec-plans/completed").mkdir(parents=True)
    (active_directory / "sample.md").write_text("# Sample\n", encoding="utf-8")

    assert find_plan_issues(tmp_path) == (
        "docs/exec-plans/active/sample.md: seção obrigatória ausente: "
        "## Progresso",
        "docs/exec-plans/active/sample.md: seção obrigatória ausente: "
        "## Surpresas e Descobertas",
        "docs/exec-plans/active/sample.md: seção obrigatória ausente: "
        "## Registro de Decisões",
        "docs/exec-plans/active/sample.md: seção obrigatória ausente: "
        "## Resultados e Retrospectiva",
    )


def test_find_plan_issues_reports_delimited_code_fences(
    tmp_path: Path,
) -> None:
    active_directory = tmp_path / "docs/exec-plans/active"
    active_directory.mkdir(parents=True)
    (tmp_path / "docs/exec-plans/completed").mkdir(parents=True)
    (active_directory / "sample.md").write_text(
        "```md\n# Sample\n```\n",
        encoding="utf-8",
    )

    assert find_plan_issues(tmp_path)[-1] == (
        "docs/exec-plans/active/sample.md: não use blocos de código "
        "delimitados."
    )
