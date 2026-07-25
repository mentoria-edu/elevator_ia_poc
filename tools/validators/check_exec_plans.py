"""Valida a estrutura mínima dos diretórios de ExecPlans."""

from __future__ import annotations

from pathlib import Path

EXEC_PLAN_DIRECTORIES = (
    Path("docs/exec-plans/active"),
    Path("docs/exec-plans/completed"),
)
REQUIRED_SECTIONS = (
    "## Progresso",
    "## Surpresas e Descobertas",
    "## Registro de Decisões",
    "## Resultados e Retrospectiva",
)


def find_missing_directories(root: Path) -> tuple[Path, ...]:
    """Retorna os diretórios obrigatórios ausentes abaixo de ``root``."""
    return tuple(
        path for path in EXEC_PLAN_DIRECTORIES if not (root / path).is_dir()
    )


def find_plan_issues(root: Path) -> tuple[str, ...]:
    """Retorna violações verificáveis da convenção de ExecPlans."""
    missing_directories = find_missing_directories(root)
    issues = [
        f"Diretório obrigatório ausente: {path}"
        for path in missing_directories
    ]
    if missing_directories:
        return tuple(issues)

    for directory in EXEC_PLAN_DIRECTORIES:
        for plan_path in sorted((root / directory).glob("*.md")):
            issues.extend(find_file_issues(root, plan_path))
    return tuple(issues)


def find_file_issues(root: Path, plan_path: Path) -> tuple[str, ...]:
    """Retorna violações da estrutura de um arquivo de ExecPlan."""
    content = plan_path.read_text(encoding="utf-8")
    relative_path = plan_path.relative_to(root)
    issues = [
        f"{relative_path}: seção obrigatória ausente: {section}"
        for section in REQUIRED_SECTIONS
        if section not in content
    ]
    if "```" in content:
        issues.append(
            f"{relative_path}: não use blocos de código delimitados."
        )
    return tuple(issues)


def main() -> int:
    """Executa a validação e retorna um código de saída convencional."""
    issues = find_plan_issues(Path.cwd())
    if not issues:
        print("ExecPlans: estrutura válida.")
        return 0

    for issue in issues:
        print(issue)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
