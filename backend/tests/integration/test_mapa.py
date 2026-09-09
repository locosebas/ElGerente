"""El índice de código generado (docs/_generado/indice-codigo.md) no debe
quedar desactualizado respecto al código.

Si este test falla: `python scripts/generar_mapa.py` y commiteá el cambio.
Ver docs/MAPA.md.
"""
from __future__ import annotations

import importlib.util
import io
from contextlib import redirect_stdout
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
GENERADOR = RAIZ / "scripts" / "generar_mapa.py"
INDICE = RAIZ / "docs" / "_generado" / "indice-codigo.md"


def _cargar_generador():
    spec = importlib.util.spec_from_file_location("generar_mapa", GENERADOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_indice_codigo_actualizado():
    esperado_antes = INDICE.read_text(encoding="utf-8")

    mod = _cargar_generador()
    with redirect_stdout(io.StringIO()):
        mod.main()  # regenera el archivo

    esperado_despues = INDICE.read_text(encoding="utf-8")
    # Restaura por si acaso (main() ya lo reescribió idéntico si estaba al día).
    INDICE.write_text(esperado_antes, encoding="utf-8")

    assert esperado_antes == esperado_despues, (
        "docs/_generado/indice-codigo.md está desactualizado. "
        "Corré: python scripts/generar_mapa.py"
    )
