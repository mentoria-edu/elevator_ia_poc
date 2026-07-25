"""Interface de linha de comando do Garbage Collector."""

import argparse
import sys
from collections.abc import Callable, Sequence
from datetime import datetime, timezone
from pathlib import Path

from tools.garbage_collector.configuration import (
    ConfigurationError,
    load_configuration,
)
from tools.garbage_collector.inventory import write_inventory
from tools.garbage_collector.models import ScanResult, Severity
from tools.garbage_collector.output_paths import OutputWriteError
from tools.garbage_collector.report import (
    write_configuration_error_report,
    write_report,
)
from tools.garbage_collector.rules import RuleApplicationError
from tools.garbage_collector.scan import (
    GitRepositoryPathProvider,
    RepositoryAccessError,
    RepositoryPathProvider,
    scan_repository,
)

DEFAULT_RULES_FILE = "docs/garbage-collector/rules/default-rules.yml"
DEFAULT_EXCEPTIONS_FILE = (
    "docs/garbage-collector/exceptions/active-exceptions.yml"
)


def main(argv: Sequence[str] | None = None) -> int:
    """Executa a CLI com dependências reais."""
    return run(
        argv,
        path_provider=GitRepositoryPathProvider(),
        now=_utc_now,
    )


def run(
    argv: Sequence[str] | None,
    *,
    path_provider: RepositoryPathProvider,
    now: Callable[[], datetime],
) -> int:
    """Executa um subcomando com dependências injetáveis."""
    arguments = _parser().parse_args(argv)
    project_root = Path(arguments.project_root).resolve()
    if not project_root.is_dir():
        _error(f"Raiz do projeto não é um diretório: {project_root}")
        return 2

    try:
        configuration = load_configuration(
            project_root,
            arguments.rules_file,
            arguments.exceptions_file,
        )
    except ConfigurationError as error:
        for message in error.errors:
            _error(message)
        if arguments.command in {"report", "check"} and error.safe_to_report:
            try:
                destination = write_configuration_error_report(
                    now(), project_root, error.errors
                )
                print(f"Relatório de erro gravado em {destination}")
            except OutputWriteError as write_error:
                _error(str(write_error))
                return 3
        return 2

    try:
        scan_result = scan_repository(
            project_root,
            configuration,
            path_provider=path_provider,
            now=now,
        )
    except (RepositoryAccessError, RuleApplicationError, ValueError) as error:
        _error(str(error))
        return 2

    try:
        _write_outputs(arguments.command, scan_result)
    except OutputWriteError as error:
        _error(str(error))
        return 3

    print(
        f"Arquivos analisados: {scan_result.scanned_files}; "
        f"candidatos: {len(scan_result.candidates)}."
    )
    if _threshold_reached(scan_result, arguments.fail_on):
        _error(f"Limiar --fail-on {arguments.fail_on} atingido.")
        return 1
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="uv run python -m tools.garbage_collector"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("scan", "inventory", "report", "check"):
        subparser = subparsers.add_parser(command)
        subparser.add_argument("--project-root", default=".")
        subparser.add_argument("--rules-file", default=DEFAULT_RULES_FILE)
        subparser.add_argument(
            "--exceptions-file", default=DEFAULT_EXCEPTIONS_FILE
        )
        subparser.add_argument(
            "--fail-on", choices=("error", "warning"), default=None
        )
    return parser


def _write_outputs(command: str, scan_result: ScanResult) -> None:
    if command in {"inventory", "check"}:
        current, historical = write_inventory(scan_result)
        print(f"Inventário atual gravado em {current}")
        print(f"Histórico gravado em {historical}")
    if command in {"report", "check"}:
        destination = write_report(scan_result)
        print(f"Relatório gravado em {destination}")


def _threshold_reached(scan_result: ScanResult, fail_on: str | None) -> bool:
    severities = {candidate.severity for candidate in scan_result.candidates}
    if fail_on == "error":
        return Severity.ERROR in severities
    if fail_on == "warning":
        return bool(
            severities.intersection({Severity.WARNING, Severity.ERROR})
        )
    return False


def _error(message: str) -> None:
    print(f"Erro: {message}", file=sys.stderr)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)
