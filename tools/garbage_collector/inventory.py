"""Serialização e persistência do inventário de manutenção."""

from collections.abc import Mapping
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import cast

import yaml

from tools.garbage_collector.models import (
    InventoryEntry,
    InventoryStatus,
    RecommendedAction,
    ScanResult,
    Severity,
)
from tools.garbage_collector.output_paths import (
    current_inventory_path,
    history_path,
    write_atomic,
    write_exclusive,
)


class InventoryValidationError(Exception):
    """Inventário serializado não pode ser lido com segurança."""


def inventory_entries(scan_result: ScanResult) -> tuple[InventoryEntry, ...]:
    """Converte candidatos em entradas pendentes de revisão."""
    return tuple(
        InventoryEntry(
            path=candidate.path,
            rule_id=candidate.rule_id,
            description=candidate.description,
            severity=candidate.severity,
            recommended_action=candidate.recommended_action,
            status=InventoryStatus.PENDING_REVIEW,
            last_modified=candidate.last_modified,
            evidence=candidate.evidence,
        )
        for candidate in scan_result.candidates
    )


def serialize_inventory(scan_result: ScanResult) -> str:
    """Produz YAML determinístico que representa somente a execução atual."""
    document = {
        "version": 1,
        "generated_at": _timestamp(scan_result.generated_at),
        "project_root": ".",
        "rules_version": scan_result.rules_version,
        "scanned_files": scan_result.scanned_files,
        "items": [
            {
                "path": entry.path.as_posix(),
                "rule_id": entry.rule_id,
                "description": entry.description,
                "severity": entry.severity.value,
                "recommended_action": entry.recommended_action.value,
                "status": entry.status.value,
                "last_modified": (
                    _timestamp(entry.last_modified)
                    if entry.last_modified is not None
                    else None
                ),
                "evidence": [
                    {
                        "criterion": evidence.criterion,
                        "value": evidence.value,
                    }
                    for evidence in entry.evidence
                ],
            }
            for entry in inventory_entries(scan_result)
        ],
    }
    return yaml.safe_dump(
        document,
        allow_unicode=True,
        sort_keys=False,
    )


def write_inventory(scan_result: ScanResult) -> tuple[Path, Path]:
    """Grava histórico exclusivo e inventário atual validado."""
    content = serialize_inventory(scan_result)
    validate_inventory(
        content,
        known_rule_ids=frozenset(
            candidate.rule_id for candidate in scan_result.candidates
        ),
    )
    history_filename = scan_result.generated_at.strftime(
        "%Y-%m-%dT%H%M%SZ.yml"
    )
    historical = history_path(scan_result.project_root, history_filename)
    current = current_inventory_path(scan_result.project_root)
    write_exclusive(historical, content)
    write_atomic(current, content)
    return current, historical


def validate_inventory(
    content: str,
    *,
    known_rule_ids: frozenset[str] | None = None,
) -> None:
    """Confirma que a serialização contém o contrato mínimo e itens únicos."""
    try:
        raw_document = cast(object, yaml.safe_load(content))
    except yaml.YAMLError as error:
        raise InventoryValidationError(
            f"Inventário contém YAML inválido: {error}"
        ) from error
    if not isinstance(raw_document, dict):
        raise InventoryValidationError("Inventário deve ser um mapa YAML.")
    document = cast(Mapping[object, object], raw_document)
    if document.get("version") != 1:
        raise InventoryValidationError("Inventário deve possuir version 1.")
    _validate_inventory_header(document)
    raw_items = document.get("items")
    if not isinstance(raw_items, list):
        raise InventoryValidationError("Inventário deve possuir lista items.")
    paths_and_rules: set[tuple[str, str]] = set()
    ordered_identities: list[tuple[str, str]] = []
    for index, raw_item in enumerate(cast(list[object], raw_items)):
        if not isinstance(raw_item, dict):
            raise InventoryValidationError(
                f"Inventário items[{index}] deve ser um mapa."
            )
        item = cast(Mapping[object, object], raw_item)
        path = item.get("path")
        rule_id = item.get("rule_id")
        if not isinstance(path, str) or not isinstance(rule_id, str):
            raise InventoryValidationError(
                f"Inventário items[{index}] deve possuir path e rule_id."
            )
        normalized_path = PurePosixPath(path)
        if (
            normalized_path.is_absolute()
            or ".." in normalized_path.parts
            or normalized_path.as_posix() != path
        ):
            raise InventoryValidationError(
                f"Inventário items[{index}] possui caminho inválido: {path}."
            )
        if known_rule_ids is not None and rule_id not in known_rule_ids:
            raise InventoryValidationError(
                f"Inventário items[{index}] referencia regra desconhecida: "
                f"{rule_id}."
            )
        _validate_inventory_item(item, index)
        identity = (path, rule_id)
        if identity in paths_and_rules:
            raise InventoryValidationError(
                f"Inventário possui entrada duplicada: {identity}."
            )
        paths_and_rules.add(identity)
        ordered_identities.append(identity)
    if ordered_identities != sorted(ordered_identities):
        raise InventoryValidationError(
            "Inventário deve ordenar itens por path e rule_id."
        )


def _validate_inventory_header(
    document: Mapping[object, object],
) -> None:
    required_types = {
        "generated_at": str,
        "project_root": str,
        "rules_version": int,
        "scanned_files": int,
    }
    for field, expected_type in required_types.items():
        if not isinstance(document.get(field), expected_type):
            raise InventoryValidationError(
                f"Inventário deve possuir {field} no tipo esperado."
            )


def _validate_inventory_item(
    item: Mapping[object, object],
    index: int,
) -> None:
    description = item.get("description")
    if not isinstance(description, str) or not description:
        raise InventoryValidationError(
            f"Inventário items[{index}] deve possuir description."
        )
    _validate_enum_field(item, "severity", Severity, index)
    _validate_enum_field(item, "recommended_action", RecommendedAction, index)
    _validate_enum_field(item, "status", InventoryStatus, index)
    last_modified = item.get("last_modified")
    if last_modified is not None and not isinstance(last_modified, str):
        raise InventoryValidationError(
            f"Inventário items[{index}].last_modified deve ser texto ou null."
        )
    evidence = item.get("evidence")
    if not isinstance(evidence, list):
        raise InventoryValidationError(
            f"Inventário items[{index}].evidence deve ser lista."
        )
    for evidence_index, raw_evidence in enumerate(
        cast(list[object], evidence)
    ):
        if not isinstance(raw_evidence, dict):
            raise InventoryValidationError(
                f"Inventário items[{index}].evidence[{evidence_index}] "
                "deve ser mapa."
            )
        evidence_item = cast(Mapping[object, object], raw_evidence)
        if not all(
            isinstance(evidence_item.get(field), str)
            and bool(evidence_item.get(field))
            for field in ("criterion", "value")
        ):
            raise InventoryValidationError(
                f"Inventário items[{index}].evidence[{evidence_index}] "
                "deve possuir criterion e value."
            )


def _validate_enum_field(
    item: Mapping[object, object],
    field: str,
    enum_type: type[Severity]
    | type[RecommendedAction]
    | type[InventoryStatus],
    index: int,
) -> None:
    value = item.get(field)
    supported = {member.value for member in enum_type}
    if value not in supported:
        raise InventoryValidationError(
            f"Inventário items[{index}].{field} possui valor inválido: "
            f"{value}."
        )


def _timestamp(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")
