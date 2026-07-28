"""Carregamento e validação das configurações YAML."""

from collections.abc import Mapping
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import cast

import yaml

from tools.garbage_collector.models import (
    ActiveException,
    GarbageCollectorConfiguration,
    InspectionRule,
    RecommendedAction,
    Severity,
)

SUPPORTED_VERSION = 1
RULE_FIELDS = frozenset({
    "id",
    "description",
    "severity",
    "action",
    "path",
    "extensions",
    "patterns",
    "max_age_days",
    "tracked_only",
})
EXCEPTION_FIELDS = frozenset({"path", "reason", "owner", "removal_condition"})


class ConfigurationError(Exception):
    """Erros encontrados sem modificar a configuração de origem."""

    def __init__(
        self, errors: tuple[str, ...], *, safe_to_report: bool = True
    ) -> None:
        super().__init__("; ".join(errors))
        self.errors = errors
        self.safe_to_report = safe_to_report


def load_configuration(
    project_root: Path,
    rules_file: str,
    exceptions_file: str,
) -> GarbageCollectorConfiguration:
    """Carrega regras e exceções e informa todos os erros encontrados."""
    errors: list[str] = []
    safety_errors: list[str] = []
    rules_path = _configuration_path(
        project_root, rules_file, "arquivo de regras", errors, safety_errors
    )
    exceptions_path = _configuration_path(
        project_root,
        exceptions_file,
        "arquivo de exceções",
        errors,
        safety_errors,
    )

    rules_document = _read_yaml(rules_path, "regras", errors)
    exceptions_document = _read_yaml(exceptions_path, "exceções", errors)
    rules_version, rules = _parse_rules(
        rules_document, project_root, errors, safety_errors
    )
    exceptions_version, exceptions = _parse_exceptions(
        exceptions_document, project_root, errors, safety_errors
    )

    if errors:
        raise ConfigurationError(
            tuple(errors), safe_to_report=not safety_errors
        )
    return GarbageCollectorConfiguration(
        rules_version=rules_version,
        exceptions_version=exceptions_version,
        rules=tuple(rules),
        exceptions=tuple(exceptions),
    )


def normalize_relative_path(
    value: str,
    field_name: str,
    errors: list[str],
    safety_errors: list[str],
) -> PurePosixPath | None:
    """Normaliza um caminho ou registra por que ele não é seguro."""
    if not value.strip():
        errors.append(f"{field_name}: esperado texto não vazio.")
        return None
    if "\\" in value or PureWindowsPath(value).is_absolute():
        message = (
            f"{field_name}: caminho deve ser relativo e usar '/': {value}"
        )
        errors.append(message)
        safety_errors.append(message)
        return None
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts:
        message = f"{field_name}: caminho deve permanecer na raiz: {value}"
        errors.append(message)
        safety_errors.append(message)
        return None
    normalized = PurePosixPath(*(part for part in path.parts if part != "."))
    if not normalized.parts:
        return PurePosixPath(".")
    return normalized


def resolve_inside_root(
    project_root: Path,
    relative_path: PurePosixPath,
    field_name: str,
    errors: list[str],
    safety_errors: list[str],
) -> Path | None:
    """Resolve um caminho sem permitir que links escapem da raiz."""
    root = project_root.resolve()
    resolved = (root / Path(*relative_path.parts)).resolve(strict=False)
    if not resolved.is_relative_to(root):
        message = (
            f"{field_name}: caminho resolve fora da raiz: {relative_path}"
        )
        errors.append(message)
        safety_errors.append(message)
        return None
    return resolved


def _configuration_path(
    project_root: Path,
    value: str,
    field_name: str,
    errors: list[str],
    safety_errors: list[str],
) -> Path | None:
    relative = normalize_relative_path(
        value, field_name, errors, safety_errors
    )
    if relative is None:
        return None
    return resolve_inside_root(
        project_root, relative, field_name, errors, safety_errors
    )


def _read_yaml(
    path: Path | None, label: str, errors: list[str]
) -> object | None:
    if path is None:
        return None
    if not path.is_file():
        errors.append(f"Configuração de {label} não encontrada: {path}")
        return None
    try:
        return cast(object, yaml.safe_load(path.read_text(encoding="utf-8")))
    except (OSError, UnicodeError, yaml.YAMLError) as error:
        errors.append(f"Não foi possível ler configuração de {label}: {error}")
        return None


def _mapping(
    value: object, label: str, errors: list[str]
) -> Mapping[object, object] | None:
    if not isinstance(value, dict):
        errors.append(f"{label}: esperado mapa YAML.")
        return None
    return cast(Mapping[object, object], value)


def _version(
    document: Mapping[object, object],
    label: str,
    errors: list[str],
) -> int:
    value = document.get("version")
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or value != SUPPORTED_VERSION
    ):
        errors.append(
            f"{label}.version: esperado inteiro {SUPPORTED_VERSION}."
        )
        return SUPPORTED_VERSION
    return value


def _parse_rules(
    value: object | None,
    project_root: Path,
    errors: list[str],
    safety_errors: list[str],
) -> tuple[int, list[InspectionRule]]:
    if value is None:
        return SUPPORTED_VERSION, []
    document = _mapping(value, "regras", errors)
    if document is None:
        return SUPPORTED_VERSION, []
    version = _version(document, "regras", errors)
    raw_rules = document.get("rules")
    if not isinstance(raw_rules, list):
        errors.append("regras.rules: esperada lista.")
        return version, []

    rules: list[InspectionRule] = []
    identifiers: set[str] = set()
    for index, raw_rule in enumerate(cast(list[object], raw_rules)):
        rule = _parse_rule(
            raw_rule,
            index,
            project_root,
            identifiers,
            errors,
            safety_errors,
        )
        if rule is not None:
            rules.append(rule)
    return version, rules


def _parse_rule(
    value: object,
    index: int,
    project_root: Path,
    identifiers: set[str],
    errors: list[str],
    safety_errors: list[str],
) -> InspectionRule | None:
    prefix = f"regras.rules[{index}]"
    document = _mapping(value, prefix, errors)
    if document is None:
        return None
    keys = {key for key in document if isinstance(key, str)}
    unknown = keys - RULE_FIELDS
    if unknown:
        errors.append(f"{prefix}: campos desconhecidos: {sorted(unknown)}")

    identifier = _required_text(document, "id", prefix, errors)
    description = _required_text(document, "description", prefix, errors)
    if identifier and identifier in identifiers:
        errors.append(f"{prefix}.id: identificador duplicado: {identifier}")
    elif identifier:
        identifiers.add(identifier)

    severity = _severity_value(document, prefix, errors)
    action = _action_value(document, prefix, errors)
    path = _optional_rule_path(
        document, prefix, project_root, errors, safety_errors
    )
    extensions = _text_list(
        document, "extensions", prefix, errors, extension=True
    )
    patterns = _text_list(document, "patterns", prefix, errors)
    max_age_days = _optional_age(document, prefix, errors)
    tracked_only = _optional_boolean(document, "tracked_only", prefix, errors)

    if "path" not in document and "patterns" not in document:
        errors.append(f"{prefix}: informe ao menos path ou patterns.")
    if (
        identifier is None
        or description is None
        or severity is None
        or action is None
    ):
        return None
    return InspectionRule(
        id=identifier,
        description=description,
        severity=severity,
        action=action,
        path=path,
        extensions=extensions,
        patterns=patterns,
        max_age_days=max_age_days,
        tracked_only=tracked_only,
    )


def _parse_exceptions(
    value: object | None,
    project_root: Path,
    errors: list[str],
    safety_errors: list[str],
) -> tuple[int, list[ActiveException]]:
    if value is None:
        return SUPPORTED_VERSION, []
    document = _mapping(value, "exceções", errors)
    if document is None:
        return SUPPORTED_VERSION, []
    version = _version(document, "exceções", errors)
    raw_exceptions = document.get("exceptions")
    if not isinstance(raw_exceptions, list):
        errors.append("exceções.exceptions: esperada lista.")
        return version, []

    exceptions: list[ActiveException] = []
    paths: set[PurePosixPath] = set()
    for index, raw_exception in enumerate(cast(list[object], raw_exceptions)):
        exception = _parse_exception(
            raw_exception, index, project_root, errors, safety_errors
        )
        if exception is None:
            continue
        if exception.path in paths:
            errors.append(
                "exceções.exceptions"
                f"[{index}].path: caminho duplicado: {exception.path}"
            )
            continue
        paths.add(exception.path)
        exceptions.append(exception)
    return version, exceptions


def _parse_exception(
    value: object,
    index: int,
    project_root: Path,
    errors: list[str],
    safety_errors: list[str],
) -> ActiveException | None:
    prefix = f"exceções.exceptions[{index}]"
    document = _mapping(value, prefix, errors)
    if document is None:
        return None
    keys = {key for key in document if isinstance(key, str)}
    unknown = keys - EXCEPTION_FIELDS
    if unknown:
        errors.append(f"{prefix}: campos não suportados: {sorted(unknown)}")

    raw_path = _required_text(document, "path", prefix, errors)
    reason = _required_text(document, "reason", prefix, errors)
    owner = _required_text(document, "owner", prefix, errors)
    removal = _required_text(document, "removal_condition", prefix, errors)
    path = None
    if raw_path:
        path = normalize_relative_path(
            raw_path, f"{prefix}.path", errors, safety_errors
        )
        if path is not None:
            resolved = resolve_inside_root(
                project_root,
                path,
                f"{prefix}.path",
                errors,
                safety_errors,
            )
            if resolved is not None and not resolved.exists():
                errors.append(
                    f"{prefix}.path: caminho não existe: {path.as_posix()}"
                )
    if path is None or reason is None or owner is None or removal is None:
        return None
    return ActiveException(
        path=path,
        reason=reason,
        owner=owner,
        removal_condition=removal,
    )


def _required_text(
    document: Mapping[object, object],
    key: str,
    prefix: str,
    errors: list[str],
) -> str | None:
    value = document.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{prefix}.{key}: esperado texto não vazio.")
        return None
    return value.strip()


def _severity_value(
    document: Mapping[object, object],
    prefix: str,
    errors: list[str],
) -> Severity | None:
    value = document.get("severity")
    if not isinstance(value, str):
        supported = ", ".join(item.value for item in Severity)
        errors.append(f"{prefix}.severity: esperado um de: {supported}.")
        return None
    try:
        return Severity(value)
    except ValueError:
        supported = ", ".join(item.value for item in Severity)
        errors.append(f"{prefix}.severity: esperado um de: {supported}.")
        return None


def _action_value(
    document: Mapping[object, object],
    prefix: str,
    errors: list[str],
) -> RecommendedAction | None:
    value = document.get("action")
    if not isinstance(value, str):
        supported = ", ".join(item.value for item in RecommendedAction)
        errors.append(f"{prefix}.action: esperado um de: {supported}.")
        return None
    try:
        return RecommendedAction(value)
    except ValueError:
        supported = ", ".join(item.value for item in RecommendedAction)
        errors.append(f"{prefix}.action: esperado um de: {supported}.")
        return None


def _optional_rule_path(
    document: Mapping[object, object],
    prefix: str,
    project_root: Path,
    errors: list[str],
    safety_errors: list[str],
) -> PurePosixPath | None:
    if "path" not in document:
        return None
    raw_path = document.get("path")
    if not isinstance(raw_path, str):
        errors.append(f"{prefix}.path: esperado texto.")
        return None
    path = normalize_relative_path(
        raw_path, f"{prefix}.path", errors, safety_errors
    )
    if path is None:
        return None
    resolved = resolve_inside_root(
        project_root, path, f"{prefix}.path", errors, safety_errors
    )
    if resolved is not None and not resolved.exists():
        errors.append(f"{prefix}.path: caminho não existe: {path.as_posix()}")
    return path


def _text_list(
    document: Mapping[object, object],
    key: str,
    prefix: str,
    errors: list[str],
    *,
    extension: bool = False,
) -> tuple[str, ...]:
    if key not in document:
        return ()
    value = document.get(key)
    if not isinstance(value, list):
        errors.append(f"{prefix}.{key}: esperada lista de textos.")
        return ()
    result: list[str] = []
    for index, item in enumerate(cast(list[object], value)):
        if not isinstance(item, str) or not item.strip():
            errors.append(
                f"{prefix}.{key}[{index}]: esperado texto não vazio."
            )
            continue
        normalized = item.strip()
        if extension and (
            not normalized.startswith(".")
            or "/" in normalized
            or "\\" in normalized
        ):
            errors.append(
                f"{prefix}.{key}[{index}]: extensão inválida: {item}"
            )
            continue
        result.append(normalized)
    return tuple(result)


def _optional_age(
    document: Mapping[object, object], prefix: str, errors: list[str]
) -> int | None:
    if "max_age_days" not in document:
        return None
    value = document.get("max_age_days")
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        errors.append(
            f"{prefix}.max_age_days: esperado inteiro maior ou igual a zero."
        )
        return None
    return value


def _optional_boolean(
    document: Mapping[object, object],
    key: str,
    prefix: str,
    errors: list[str],
) -> bool:
    if key not in document:
        return False
    value = document.get(key)
    if not isinstance(value, bool):
        errors.append(f"{prefix}.{key}: esperado booleano.")
        return False
    return value
