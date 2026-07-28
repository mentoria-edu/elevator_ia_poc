"""Testes da varredura declarativa."""

import os
from datetime import timedelta
from pathlib import Path, PurePosixPath

from tests.garbage_collector.helpers import (
    FIXED_NOW,
    FakeRepositoryPathProvider,
    fixed_now,
)
from tools.garbage_collector.models import (
    ActiveException,
    GarbageCollectorConfiguration,
    InspectionRule,
    RecommendedAction,
    Severity,
)
from tools.garbage_collector.scan import scan_repository


def _rule(**changes: object) -> InspectionRule:
    values = {
        "id": "temporary",
        "description": "Arquivo temporário",
        "severity": Severity.WARNING,
        "action": RecommendedAction.REVIEW,
        "patterns": ("*.tmp",),
        "tracked_only": True,
    }
    values.update(changes)
    return InspectionRule(**values)  # type: ignore[arg-type]


def _configuration(
    rules: tuple[InspectionRule, ...],
    exceptions: tuple[ActiveException, ...] = (),
) -> GarbageCollectorConfiguration:
    return GarbageCollectorConfiguration(
        rules_version=1,
        exceptions_version=1,
        rules=rules,
        exceptions=exceptions,
    )


def test_scan_applies_tracking_patterns_and_ordering(
    tmp_path: Path,
) -> None:
    provider = FakeRepositoryPathProvider(
        visible=("z.tmp", "ignored.tmp", "a.tmp"),
        tracked=("z.tmp", "a.tmp"),
    )

    result = scan_repository(
        tmp_path,
        _configuration((_rule(),)),
        path_provider=provider,
        now=fixed_now,
    )

    assert [candidate.path.as_posix() for candidate in result.candidates] == [
        "a.tmp",
        "z.tmp",
    ]
    assert result.scanned_files == 3
    assert result.candidates[0].evidence[-1].value == "*.tmp"


def test_scan_exception_hides_only_exact_path(tmp_path: Path) -> None:
    provider = FakeRepositoryPathProvider(
        visible=("kept.tmp", "other.tmp"),
        tracked=("kept.tmp", "other.tmp"),
    )
    exception = ActiveException(
        path=PurePosixPath("kept.tmp"),
        reason="Mantido",
        owner="equipe",
        removal_condition="Depois",
    )

    result = scan_repository(
        tmp_path,
        _configuration((_rule(),), (exception,)),
        path_provider=provider,
        now=fixed_now,
    )

    assert tuple(
        candidate.path.as_posix() for candidate in result.candidates
    ) == ("other.tmp",)


def test_scan_uses_strict_age_limit_and_records_evidence(
    tmp_path: Path,
) -> None:
    reports = tmp_path / "reports"
    reports.mkdir()
    exact = reports / "2026_06_25_scan.md"
    stale = reports / "2026_06_24_scan.md"
    exact.write_text("exact", encoding="utf-8")
    stale.write_text("stale", encoding="utf-8")
    exact_timestamp = (FIXED_NOW - timedelta(days=30)).timestamp()
    stale_timestamp = (FIXED_NOW - timedelta(days=31)).timestamp()
    os.utime(exact, (exact_timestamp, exact_timestamp))
    os.utime(stale, (stale_timestamp, stale_timestamp))
    provider = FakeRepositoryPathProvider(
        visible=(
            "reports/2026_06_25_scan.md",
            "reports/2026_06_24_scan.md",
        )
    )
    rule = _rule(
        id="stale",
        path=PurePosixPath("reports"),
        patterns=("????_??_??_scan.md",),
        extensions=(".md",),
        max_age_days=30,
        tracked_only=False,
    )

    result = scan_repository(
        tmp_path,
        _configuration((rule,)),
        path_provider=provider,
        now=fixed_now,
    )

    assert len(result.candidates) == 1
    assert result.candidates[0].path.name == "2026_06_24_scan.md"
    assert result.candidates[0].last_modified is not None
    assert ("age_days", "31") in {
        (evidence.criterion, evidence.value)
        for evidence in result.candidates[0].evidence
    }


def test_scan_does_not_modify_files(tmp_path: Path) -> None:
    marker = tmp_path / "marker.txt"
    marker.write_text("unchanged", encoding="utf-8")
    provider = FakeRepositoryPathProvider(visible=("marker.txt",))

    scan_repository(
        tmp_path,
        _configuration((_rule(tracked_only=False),)),
        path_provider=provider,
        now=fixed_now,
    )

    assert marker.read_text(encoding="utf-8") == "unchanged"
