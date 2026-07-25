"""Testes das saídas permitidas."""

from pathlib import Path, PurePosixPath

import pytest

from tests.garbage_collector.helpers import FIXED_NOW
from tools.garbage_collector.inventory import (
    InventoryValidationError,
    serialize_inventory,
    validate_inventory,
    write_inventory,
)
from tools.garbage_collector.models import (
    Candidate,
    Evidence,
    RecommendedAction,
    ScanResult,
    Severity,
)
from tools.garbage_collector.output_paths import OutputWriteError
from tools.garbage_collector.report import render_report, write_report


def _scan_result(project_root: Path) -> ScanResult:
    candidate = Candidate(
        path=PurePosixPath("artifact.tmp"),
        rule_id="temporary",
        description="Arquivo temporário",
        severity=Severity.WARNING,
        recommended_action=RecommendedAction.REVIEW,
        last_modified=None,
        evidence=(Evidence("pattern", "*.tmp"),),
    )
    return ScanResult(
        generated_at=FIXED_NOW,
        project_root=project_root,
        rules_version=1,
        scanned_files=4,
        candidates=(candidate,),
    )


def test_inventory_round_trip_and_history_are_generated(
    tmp_path: Path,
) -> None:
    result = _scan_result(tmp_path)

    current, historical = write_inventory(result)

    assert current.is_file()
    assert historical.is_file()
    assert current.read_text(encoding="utf-8") == historical.read_text(
        encoding="utf-8"
    )
    validate_inventory(current.read_text(encoding="utf-8"))


def test_inventory_history_is_never_overwritten(tmp_path: Path) -> None:
    result = _scan_result(tmp_path)
    write_inventory(result)

    with pytest.raises(OutputWriteError, match="saída exclusiva"):
        write_inventory(result)


def test_serialized_inventory_contains_review_status(
    tmp_path: Path,
) -> None:
    content = serialize_inventory(_scan_result(tmp_path))

    assert "status: pending_review" in content
    assert "recommended_action: review" in content
    assert "artifact.tmp" in content


def test_report_contains_statistics_evidence_and_safety_text(
    tmp_path: Path,
) -> None:
    result = _scan_result(tmp_path)
    content = render_report(result)

    assert "Arquivos analisados: `4`" in content
    assert "Resultados warning: `1`" in content
    assert "artifact.tmp" in content
    assert "pattern: `*.tmp`" in content
    assert "não autoriza exclusão automática" in content
    assert render_report(result) == content


def test_inventory_validation_rejects_duplicate_entries() -> None:
    content = (
        "version: 1\n"
        "generated_at: '2026-07-25T12:30:00Z'\n"
        "project_root: .\n"
        "rules_version: 1\n"
        "scanned_files: 1\n"
        "items:\n"
        "  - path: duplicate.tmp\n"
        "    rule_id: temporary\n"
        "    description: Temporário\n"
        "    severity: warning\n"
        "    recommended_action: review\n"
        "    status: pending_review\n"
        "    last_modified: null\n"
        "    evidence: []\n"
        "  - path: duplicate.tmp\n"
        "    rule_id: temporary\n"
        "    description: Temporário\n"
        "    severity: warning\n"
        "    recommended_action: review\n"
        "    status: pending_review\n"
        "    last_modified: null\n"
        "    evidence: []\n"
    )

    with pytest.raises(InventoryValidationError, match="duplicada"):
        validate_inventory(content)


def test_inventory_validation_rejects_invalid_enum(tmp_path: Path) -> None:
    content = serialize_inventory(_scan_result(tmp_path)).replace(
        "severity: warning", "severity: critical"
    )

    with pytest.raises(InventoryValidationError, match="severity"):
        validate_inventory(content)


def test_report_is_written_only_in_reports_directory(
    tmp_path: Path,
) -> None:
    marker = tmp_path / "marker.txt"
    marker.write_text("unchanged", encoding="utf-8")

    destination = write_report(_scan_result(tmp_path))

    assert destination.relative_to(tmp_path).as_posix() == (
        "docs/garbage-collector/reports/2026-07-25-scan.md"
    )
    assert marker.read_text(encoding="utf-8") == "unchanged"
