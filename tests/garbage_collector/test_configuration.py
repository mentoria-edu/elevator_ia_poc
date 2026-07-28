"""Testes de carregamento e validação YAML."""

from pathlib import Path

import pytest

from tests.garbage_collector.helpers import write_valid_configuration
from tools.garbage_collector.configuration import (
    ConfigurationError,
    load_configuration,
)


def test_load_configuration_returns_typed_rules(tmp_path: Path) -> None:
    write_valid_configuration(tmp_path)

    configuration = load_configuration(
        tmp_path,
        "docs/garbage_collector/rules/default_rules.yml",
        "docs/garbage_collector/exceptions/active_exceptions.yml",
    )

    assert configuration.rules_version == 1
    assert configuration.rules[0].id == "temporary"
    assert configuration.rules[0].tracked_only is True


@pytest.mark.parametrize(
    "rules",
    [
        "version: 1\nrules: [",
        "version: 1\nrules: invalid\n",
        "version: 2\nrules: []\n",
        (
            "version: 1\nrules:\n"
            "  - description: Sem identificador\n"
            "    patterns: ['*.tmp']\n"
            "    severity: warning\n"
            "    action: review\n"
        ),
        (
            "version: 1\nrules:\n"
            "  - id: duplicate\n"
            "    description: Primeira\n"
            "    patterns: ['*.tmp']\n"
            "    severity: warning\n"
            "    action: review\n"
            "  - id: duplicate\n"
            "    description: Segunda\n"
            "    patterns: ['*.bak']\n"
            "    severity: error\n"
            "    action: review\n"
        ),
        (
            "version: 1\nrules:\n"
            "  - id: invalid\n"
            "    description: Inválida\n"
            "    severity: critical\n"
            "    action: delete\n"
        ),
        (
            "version: 1\nrules:\n"
            "  - id: invalid-age\n"
            "    description: Idade inválida\n"
            "    patterns: ['*.tmp']\n"
            "    max_age_days: -1\n"
            "    severity: warning\n"
            "    action: review\n"
        ),
    ],
)
def test_load_configuration_rejects_invalid_rules(
    tmp_path: Path, rules: str
) -> None:
    write_valid_configuration(tmp_path, rules=rules)

    with pytest.raises(ConfigurationError):
        load_configuration(
            tmp_path,
            "docs/garbage_collector/rules/default_rules.yml",
            "docs/garbage_collector/exceptions/active_exceptions.yml",
        )


def test_load_configuration_accumulates_errors(tmp_path: Path) -> None:
    write_valid_configuration(
        tmp_path,
        rules=(
            "version: invalid\n"
            "rules:\n"
            "  - id: ''\n"
            "    description: ''\n"
            "    path: ../outside\n"
            "    extensions: [txt]\n"
            "    severity: invalid\n"
            "    action: invalid\n"
        ),
    )

    with pytest.raises(ConfigurationError) as captured:
        load_configuration(
            tmp_path,
            "docs/garbage_collector/rules/default_rules.yml",
            "docs/garbage_collector/exceptions/active_exceptions.yml",
        )

    assert len(captured.value.errors) >= 6
    assert captured.value.safe_to_report is False


@pytest.mark.parametrize(
    "exceptions",
    [
        "version: 1\nexceptions: [",
        "version: 1\nexceptions: invalid\n",
        (
            "version: 1\nexceptions:\n"
            "  - path: kept.txt\n"
            "    reason: Necessário\n"
            "    owner: equipe\n"
        ),
        (
            "version: 1\nexceptions:\n"
            "  - path: missing.txt\n"
            "    reason: Necessário\n"
            "    owner: equipe\n"
            "    removal_condition: Depois\n"
        ),
        (
            "version: 1\nexceptions:\n"
            "  - path: kept.txt\n"
            "    reason: Necessário\n"
            "    owner: equipe\n"
            "    removal_condition: Depois\n"
            "    expires_at: 2026-08-01\n"
        ),
        (
            "version: 1\nexceptions:\n"
            "  - path: kept.txt\n"
            "    reason: Necessário\n"
            "    owner: equipe\n"
            "    removal_condition: Depois\n"
            "  - path: kept.txt\n"
            "    reason: Duplicada\n"
            "    owner: equipe\n"
            "    removal_condition: Depois\n"
        ),
    ],
)
def test_load_configuration_rejects_invalid_exceptions(
    tmp_path: Path, exceptions: str
) -> None:
    (tmp_path / "kept.txt").write_text("kept", encoding="utf-8")
    write_valid_configuration(tmp_path, exceptions=exceptions)

    with pytest.raises(ConfigurationError):
        load_configuration(
            tmp_path,
            "docs/garbage_collector/rules/default_rules.yml",
            "docs/garbage_collector/exceptions/active_exceptions.yml",
        )


def test_load_configuration_accepts_permanent_exception(
    tmp_path: Path,
) -> None:
    (tmp_path / "kept.txt").write_text("kept", encoding="utf-8")
    write_valid_configuration(
        tmp_path,
        exceptions=(
            "version: 1\nexceptions:\n"
            "  - path: kept.txt\n"
            "    reason: Necessário\n"
            "    owner: equipe\n"
            "    removal_condition: Remover após migração\n"
        ),
    )

    configuration = load_configuration(
        tmp_path,
        "docs/garbage_collector/rules/default_rules.yml",
        "docs/garbage_collector/exceptions/active_exceptions.yml",
    )

    assert configuration.exceptions[0].path.as_posix() == "kept.txt"


def test_load_configuration_rejects_missing_files(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationError) as captured:
        load_configuration(tmp_path, "missing_rules.yml", "missing.yml")

    assert len(captured.value.errors) == 2
