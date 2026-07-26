"""Fakes e fábricas compartilhadas pelos testes do Garbage Collector."""

from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

from tools.garbage_collector.models import RepositoryPaths

FIXED_NOW = datetime(2026, 7, 25, 12, 30, tzinfo=timezone.utc)


class FakeRepositoryPathProvider:
    """Fornece uma fotografia determinística sem executar Git."""

    def __init__(
        self,
        visible: tuple[str, ...] = (),
        tracked: tuple[str, ...] = (),
    ) -> None:
        self._visible = tuple(PurePosixPath(path) for path in visible)
        self._tracked = frozenset(PurePosixPath(path) for path in tracked)
        self.requested_roots: list[Path] = []

    def list_paths(self, project_root: Path) -> RepositoryPaths:
        """Registra a raiz e retorna os caminhos configurados."""
        self.requested_roots.append(project_root)
        return RepositoryPaths(
            visible=self._visible,
            tracked=self._tracked,
        )


def fixed_now() -> datetime:
    """Retorna sempre o mesmo instante UTC."""
    return FIXED_NOW


def write_valid_configuration(
    project_root: Path,
    *,
    rules: str | None = None,
    exceptions: str | None = None,
) -> None:
    """Cria os dois arquivos de configuração padrão."""
    rules_path = (
        project_root / "docs/garbage_collector/rules/default_rules.yml"
    )
    exceptions_path = (
        project_root
        / "docs/garbage_collector/exceptions/active_exceptions.yml"
    )
    rules_path.parent.mkdir(parents=True)
    exceptions_path.parent.mkdir(parents=True)
    rules_path.write_text(
        rules
        or (
            "version: 1\n"
            "rules:\n"
            "  - id: temporary\n"
            "    description: Temporário versionado\n"
            "    patterns: ['*.tmp']\n"
            "    tracked_only: true\n"
            "    severity: warning\n"
            "    action: review\n"
        ),
        encoding="utf-8",
    )
    exceptions_path.write_text(
        exceptions or "version: 1\nexceptions: []\n",
        encoding="utf-8",
    )
