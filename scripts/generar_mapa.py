#!/usr/bin/env python3
"""Genera docs/_generado/indice-codigo.md — un índice compacto de todo el
código de backend/app: por módulo, su propósito y sus símbolos públicos con
una línea de descripción cada uno, más de qué otros módulos del proyecto
depende.

Sirve para que una sesión de mantenimiento (humana o IA) ubique el archivo y
el símbolo correcto SIN abrir cada fuente. Para la línea exacta:
    grep -n "def <nombre>" backend/app/.../<archivo>.py

Regenerar cuando parezca desactualizado:
    python scripts/generar_mapa.py
"""
from __future__ import annotations

import ast
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
APP = RAIZ / "backend" / "app"
SALIDA = RAIZ / "docs" / "_generado" / "indice-codigo.md"


def _primera_linea(texto: str | None) -> str:
    if not texto:
        return ""
    for linea in texto.strip().splitlines():
        if linea.strip():
            return linea.strip()
    return ""


def _simbolos(arbol: ast.Module) -> list[str]:
    filas: list[str] = []
    for nodo in arbol.body:
        if isinstance(nodo, ast.ClassDef):
            filas.append(f"  - `class {nodo.name}` — {_primera_linea(ast.get_docstring(nodo))}")
        elif isinstance(nodo, ast.AsyncFunctionDef | ast.FunctionDef):
            if nodo.name.startswith("_"):
                continue
            prefijo = "async def" if isinstance(nodo, ast.AsyncFunctionDef) else "def"
            args = ", ".join(a.arg for a in nodo.args.args if a.arg not in ("self", "cls"))
            filas.append(
                f"  - `{prefijo} {nodo.name}({args})` — {_primera_linea(ast.get_docstring(nodo))}"
            )
    return filas


def _deps_internas(arbol: ast.Module) -> list[str]:
    deps: set[str] = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.ImportFrom) and nodo.module and nodo.module.startswith("app."):
            deps.add(nodo.module)
    return sorted(deps)


def main() -> None:
    modulos = sorted(APP.rglob("*.py"))
    lineas: list[str] = [
        "# Índice de código (generado)",
        "",
        "> **Generado por `scripts/generar_mapa.py`. No editar a mano.**",
        "> Regenerar: `python scripts/generar_mapa.py`.",
        "",
        "Para la línea exacta de un símbolo: `grep -n \"def <nombre>\" <archivo>`.",
        "",
    ]
    for ruta in modulos:
        if ruta.name == "__init__.py" and ruta.stat().st_size == 0:
            continue
        rel = ruta.relative_to(RAIZ)
        arbol = ast.parse(ruta.read_text(encoding="utf-8"))
        lineas.append(f"## `{rel}`")
        doc = _primera_linea(ast.get_docstring(arbol))
        if doc:
            lineas.append(f"_{doc}_")
        simbolos = _simbolos(arbol)
        if simbolos:
            lineas.append("")
            lineas.extend(simbolos)
        deps = _deps_internas(arbol)
        if deps:
            lineas.append("")
            lineas.append(f"  depende de: {', '.join(f'`{d}`' for d in deps)}")
        lineas.append("")

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print(f"Escrito {SALIDA.relative_to(RAIZ)}  ({len(modulos)} módulos)")


if __name__ == "__main__":
    main()
