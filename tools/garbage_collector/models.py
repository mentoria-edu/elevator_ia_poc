"""Modelos tipados do Garbage Collector."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from pathlib import Path, PurePosixPath


class Severity(StrEnum):
    """Gravidade declarada por uma regra."""

    NONE = "none"
    WARNING = "warning"
    ERROR = "error"


class RecommendedAction(StrEnum):
    """Ação humana permitida para um candidato."""

    REVIEW = "review"


class InventoryStatus(StrEnum):
    """Estado de uma entrada do inventário."""

    PENDING_REVIEW = "pending_review"


@dataclass(frozen=True, slots=True)
class InspectionRule:
    """Critérios declarativos usados para localizar candidatos."""

    id: str
    description: str
    severity: Severity
    action: RecommendedAction
    path: PurePosixPath | None = None
    extensions: tuple[str, ...] = ()
    patterns: tuple[str, ...] = ()
    max_age_days: int | None = None
    tracked_only: bool = False


@dataclass(frozen=True, slots=True)
class ActiveException:
    """Caminho explicitamente excluído da varredura."""

    path: PurePosixPath
    reason: str
    owner: str
    removal_condition: str


@dataclass(frozen=True, slots=True)
class Evidence:
    """Fato observável que explica a seleção de um candidato."""

    criterion: str
    value: str


@dataclass(frozen=True, slots=True)
class Candidate:
    """Artefato que precisa de revisão humana."""

    path: PurePosixPath
    rule_id: str
    description: str
    severity: Severity
    recommended_action: RecommendedAction
    last_modified: datetime | None
    evidence: tuple[Evidence, ...]


@dataclass(frozen=True, slots=True)
class GarbageCollectorConfiguration:
    """Configuração validada para uma execução."""

    rules_version: int
    exceptions_version: int
    rules: tuple[InspectionRule, ...]
    exceptions: tuple[ActiveException, ...]


@dataclass(frozen=True, slots=True)
class RepositoryPaths:
    """Caminhos visíveis e caminhos versionados segundo o Git."""

    visible: tuple[PurePosixPath, ...]
    tracked: frozenset[PurePosixPath]


@dataclass(frozen=True, slots=True)
class ScanResult:
    """Resultado completo e imutável de uma varredura."""

    generated_at: datetime
    project_root: Path
    rules_version: int
    scanned_files: int
    candidates: tuple[Candidate, ...]


@dataclass(frozen=True, slots=True)
class InventoryEntry:
    """Representação persistida de um candidato."""

    path: PurePosixPath
    rule_id: str
    description: str
    severity: Severity
    recommended_action: RecommendedAction
    status: InventoryStatus
    last_modified: datetime | None
    evidence: tuple[Evidence, ...]


@dataclass(frozen=True, slots=True)
class ExecutionReport:
    """Dados tipados usados para renderizar um relatório."""

    generated_at: datetime
    project_root: Path
    rules_version: int | None
    scanned_files: int
    candidates: tuple[Candidate, ...]
    configuration_errors: tuple[str, ...] = ()
