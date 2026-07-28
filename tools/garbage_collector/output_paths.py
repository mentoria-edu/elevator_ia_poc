"""Proteção centralizada dos destinos de escrita permitidos."""

import os
import re
import tempfile
from pathlib import Path

CURRENT_INVENTORY = Path("docs/garbage_collector/inventory/inventory.yml")
INVENTORY_HISTORY = Path("docs/garbage_collector/inventory/history")
REPORTS = Path("docs/garbage_collector/reports")
HISTORY_NAME = re.compile(r"\d{4}_\d{2}_\d{2}_\d{6}z\.yml")
REPORT_NAME = re.compile(r"\d{4}_\d{2}_\d{2}_scan\.md")


class OutputWriteError(Exception):
    """Falha ao validar ou gravar uma saída permitida."""


def current_inventory_path(project_root: Path) -> Path:
    """Retorna o destino validado do inventário atual."""
    return _inside_root(project_root, CURRENT_INVENTORY)


def history_path(project_root: Path, filename: str) -> Path:
    """Retorna um histórico válido sem aceitar nomes arbitrários."""
    if HISTORY_NAME.fullmatch(filename) is None:
        raise OutputWriteError(
            f"Nome de histórico fora do formato permitido: {filename}"
        )
    return _inside_root(project_root, INVENTORY_HISTORY / filename)


def report_path(project_root: Path, filename: str) -> Path:
    """Retorna um relatório válido sem aceitar nomes arbitrários."""
    if REPORT_NAME.fullmatch(filename) is None:
        raise OutputWriteError(
            f"Nome de relatório fora do formato permitido: {filename}"
        )
    return _inside_root(project_root, REPORTS / filename)


def write_atomic(path: Path, content: str) -> None:
    """Substitui uma saída permitida por conteúdo UTF-8 completo."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_name = ""
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            delete=False,
        ) as temporary:
            temporary.write(content)
            temporary_name = temporary.name
        os.replace(temporary_name, path)
    except OSError as error:
        if temporary_name:
            try:
                os.unlink(temporary_name)
            except OSError:
                pass
        raise OutputWriteError(
            f"Não foi possível gravar saída {path}: {error}"
        ) from error


def write_exclusive(path: Path, content: str) -> None:
    """Cria uma saída histórica sem substituir conteúdo existente."""
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("x", encoding="utf-8") as output:
            output.write(content)
    except OSError as error:
        raise OutputWriteError(
            f"Não foi possível criar saída exclusiva {path}: {error}"
        ) from error


def _inside_root(project_root: Path, relative_path: Path) -> Path:
    root = project_root.resolve()
    destination = (root / relative_path).resolve(strict=False)
    if not destination.is_relative_to(root):
        raise OutputWriteError(
            f"Destino de saída fora da raiz: {relative_path}"
        )
    return destination
