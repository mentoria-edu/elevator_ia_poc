"""Varredura determinística de candidatos à revisão."""

import os
import subprocess
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Protocol

from tools.garbage_collector.models import (
    GarbageCollectorConfiguration,
    RepositoryPaths,
    ScanResult,
)
from tools.garbage_collector.rules import apply_rule


class RepositoryAccessError(Exception):
    """Falha ao enumerar o conteúdo do repositório."""


class RepositoryPathProvider(Protocol):
    """Contrato para enumerar caminhos visíveis e versionados."""

    def list_paths(self, project_root: Path) -> RepositoryPaths:
        """Retorna caminhos relativos normalizados."""


class GitRepositoryPathProvider:
    """Enumera caminhos usando comandos Git somente leitura."""

    def list_paths(self, project_root: Path) -> RepositoryPaths:
        """Consulta arquivos visíveis e arquivos rastreados."""
        visible = self._git_paths(
            project_root,
            ("ls-files", "-z", "--cached", "--others", "--exclude-standard"),
        )
        tracked = self._git_paths(project_root, ("ls-files", "-z", "--cached"))
        return RepositoryPaths(
            visible=tuple(sorted(visible, key=PurePosixPath.as_posix)),
            tracked=frozenset(tracked),
        )

    def _git_paths(
        self, project_root: Path, arguments: tuple[str, ...]
    ) -> set[PurePosixPath]:
        process = subprocess.run(
            ("git", "-C", os.fspath(project_root), *arguments),
            check=False,
            capture_output=True,
        )
        if process.returncode != 0:
            message = os.fsdecode(process.stderr).strip()
            raise RepositoryAccessError(
                f"Git não conseguiu enumerar o repositório: {message}"
            )
        return {
            PurePosixPath(os.fsdecode(raw_path))
            for raw_path in process.stdout.split(b"\0")
            if raw_path
        }


def scan_repository(
    project_root: Path,
    configuration: GarbageCollectorConfiguration,
    *,
    path_provider: RepositoryPathProvider | None = None,
    now: Callable[[], datetime] | None = None,
) -> ScanResult:
    """Aplica todas as regras sem modificar o repositório."""
    root = project_root.resolve()
    reference_time = (now or _utc_now)()
    if reference_time.tzinfo is None:
        raise ValueError("O relógio deve retornar datetime com fuso horário.")
    reference_time = reference_time.astimezone(timezone.utc)
    repository_paths = (
        path_provider or GitRepositoryPathProvider()
    ).list_paths(root)
    exceptions = {exception.path for exception in configuration.exceptions}
    candidates = {}

    for rule in configuration.rules:
        for path in repository_paths.visible:
            if path in exceptions:
                continue
            candidate = apply_rule(
                root,
                path,
                rule,
                reference_time,
                tracked=path in repository_paths.tracked,
            )
            if candidate is not None:
                candidates[(candidate.path, candidate.rule_id)] = candidate

    ordered = tuple(
        sorted(
            candidates.values(),
            key=lambda candidate: (
                candidate.path.as_posix(),
                candidate.rule_id,
            ),
        )
    )
    return ScanResult(
        generated_at=reference_time,
        project_root=root,
        rules_version=configuration.rules_version,
        scanned_files=len(repository_paths.visible),
        candidates=ordered,
    )


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)
