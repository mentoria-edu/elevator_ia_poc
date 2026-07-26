"""Geração determinística de relatórios de manutenção."""

from collections.abc import Sequence
from datetime import datetime
from pathlib import Path

from tools.garbage_collector.models import (
    ExecutionReport,
    ScanResult,
    Severity,
)
from tools.garbage_collector.output_paths import report_path, write_atomic


def render_report(scan_result: ScanResult) -> str:
    """Renderiza um relatório Markdown para revisão humana."""
    report = ExecutionReport(
        generated_at=scan_result.generated_at,
        project_root=scan_result.project_root,
        rules_version=scan_result.rules_version,
        scanned_files=scan_result.scanned_files,
        candidates=scan_result.candidates,
    )
    return _render_execution_report(report)


def _render_execution_report(report: ExecutionReport) -> str:
    """Converte os dados tipados do relatório em Markdown."""
    errors = sum(
        candidate.severity is Severity.ERROR for candidate in report.candidates
    )
    warnings = sum(
        candidate.severity is Severity.WARNING
        for candidate in report.candidates
    )
    lines = _report_header(
        generated_at=report.generated_at,
        project_root=report.project_root,
        rules_version=str(report.rules_version),
        scanned_files=report.scanned_files,
        candidates=len(report.candidates),
        errors=errors,
        warnings=warnings,
    )
    lines.extend([
        "",
        "## Candidatos",
        "",
        "| Caminho | Regra | Severidade | Motivo | Ação |",
        "| --- | --- | --- | --- | --- |",
    ])
    if report.candidates:
        for candidate in report.candidates:
            lines.append(
                "| "
                + " | ".join((
                    _cell(candidate.path.as_posix()),
                    _cell(candidate.rule_id),
                    candidate.severity.value,
                    _cell(candidate.description),
                    candidate.recommended_action.value,
                ))
                + " |"
            )
    else:
        lines.append("| _Nenhum_ | - | - | - | - |")

    lines.extend(["", "## Evidências", ""])
    if report.candidates:
        for candidate in report.candidates:
            lines.append(
                f"### `{candidate.path.as_posix()}` / `{candidate.rule_id}`"
            )
            lines.append("")
            for evidence in candidate.evidence:
                lines.append(f"- {evidence.criterion}: `{evidence.value}`")
            if candidate.last_modified is not None:
                lines.append(
                    f"- last_modified: `{_timestamp(candidate.last_modified)}`"
                )
            lines.append("")
    else:
        lines.extend(["Nenhuma evidência foi produzida.", ""])
    lines.extend(_next_steps())
    return "\n".join(lines).rstrip() + "\n"


def render_configuration_error_report(
    generated_at: datetime,
    project_root: Path,
    errors: Sequence[str],
) -> str:
    """Registra erros de configuração sem afirmar que houve varredura."""
    report = ExecutionReport(
        generated_at=generated_at,
        project_root=project_root,
        rules_version=None,
        scanned_files=0,
        candidates=(),
        configuration_errors=tuple(errors),
    )
    lines = _report_header(
        generated_at=report.generated_at,
        project_root=report.project_root,
        rules_version="indisponível",
        scanned_files=report.scanned_files,
        candidates=0,
        errors=len(report.configuration_errors),
        warnings=0,
    )
    lines.extend(["", "## Erros de configuração", ""])
    lines.extend(
        f"- {_escape_text(error)}" for error in report.configuration_errors
    )
    lines.extend(["", *_next_steps()])
    return "\n".join(lines).rstrip() + "\n"


def write_report(scan_result: ScanResult) -> Path:
    """Grava o relatório diário no único diretório permitido."""
    filename = scan_result.generated_at.strftime("%Y_%m_%d_scan.md")
    destination = report_path(scan_result.project_root, filename)
    write_atomic(destination, render_report(scan_result))
    return destination


def write_configuration_error_report(
    generated_at: datetime,
    project_root: Path,
    errors: Sequence[str],
) -> Path:
    """Grava um relatório diário de configuração inválida."""
    filename = generated_at.strftime("%Y_%m_%d_scan.md")
    destination = report_path(project_root, filename)
    content = render_configuration_error_report(
        generated_at, project_root, errors
    )
    write_atomic(destination, content)
    return destination


def _report_header(
    *,
    generated_at: datetime,
    project_root: Path,
    rules_version: str,
    scanned_files: int,
    candidates: int,
    errors: int,
    warnings: int,
) -> list[str]:
    return [
        "# Relatório do Garbage Collector",
        "",
        f"- Execução: `{_timestamp(generated_at)}`",
        f"- Raiz analisada: `{_display_root(project_root)}`",
        f"- Versão das regras: `{rules_version}`",
        f"- Arquivos analisados: `{scanned_files}`",
        f"- Candidatos: `{candidates}`",
        f"- Resultados error: `{errors}`",
        f"- Resultados warning: `{warnings}`",
    ]


def _next_steps() -> list[str]:
    return [
        "## Próximos passos",
        "",
        "Revise cada candidato e sua evidência. Qualquer alteração deve ser "
        "feita explicitamente por uma pessoa e seguir o fluxo de revisão do "
        "repositório. Este relatório não autoriza exclusão automática.",
    ]


def _timestamp(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def _display_root(project_root: Path) -> str:
    return "." if project_root.is_absolute() else project_root.as_posix()


def _cell(value: str) -> str:
    return _escape_text(value).replace("|", r"\|")


def _escape_text(value: str) -> str:
    return value.replace("\r", " ").replace("\n", " ")
