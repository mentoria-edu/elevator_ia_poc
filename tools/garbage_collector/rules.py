"""Aplicação dos critérios declarados pelas regras."""

import fnmatch
import os
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

from tools.garbage_collector.models import (
    Candidate,
    Evidence,
    InspectionRule,
)


class RuleApplicationError(Exception):
    """Falha observada ao inspecionar um caminho enumerado."""


def apply_rule(
    project_root: Path,
    path: PurePosixPath,
    rule: InspectionRule,
    reference_time: datetime,
    *,
    tracked: bool,
) -> Candidate | None:
    """Retorna um candidato quando todos os critérios da regra coincidem."""
    evidence: list[Evidence] = []
    if rule.path is not None and not _is_in_scope(path, rule.path):
        return None
    if rule.path is not None:
        evidence.append(Evidence("path", rule.path.as_posix()))
    if rule.tracked_only and not tracked:
        return None
    if rule.tracked_only:
        evidence.append(Evidence("tracked", "true"))
    if rule.extensions and path.suffix not in rule.extensions:
        return None
    if rule.extensions:
        evidence.append(Evidence("extension", path.suffix))

    matched_pattern = _matched_pattern(path, rule.patterns)
    if rule.patterns and matched_pattern is None:
        return None
    if matched_pattern is not None:
        evidence.append(Evidence("pattern", matched_pattern))

    last_modified = None
    if rule.max_age_days is not None:
        last_modified = _last_modified(project_root, path)
        age_days = (reference_time - last_modified).total_seconds() / 86_400
        if age_days <= rule.max_age_days:
            return None
        evidence.append(Evidence("age_days", str(int(age_days))))

    return Candidate(
        path=path,
        rule_id=rule.id,
        description=rule.description,
        severity=rule.severity,
        recommended_action=rule.action,
        last_modified=last_modified,
        evidence=tuple(evidence),
    )


def _is_in_scope(path: PurePosixPath, scope: PurePosixPath) -> bool:
    return path == scope or scope in path.parents


def _matched_pattern(
    path: PurePosixPath, patterns: tuple[str, ...]
) -> str | None:
    for pattern in patterns:
        if fnmatch.fnmatchcase(path.as_posix(), pattern):
            return pattern
        if fnmatch.fnmatchcase(path.name, pattern):
            return pattern
        if any(fnmatch.fnmatchcase(part, pattern) for part in path.parts):
            return pattern
    return None


def _last_modified(project_root: Path, path: PurePosixPath) -> datetime:
    absolute_path = project_root / Path(*path.parts)
    try:
        timestamp = os.lstat(absolute_path).st_mtime
    except OSError as error:
        raise RuleApplicationError(
            f"Não foi possível ler data de modificação de {path}: {error}"
        ) from error
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)
