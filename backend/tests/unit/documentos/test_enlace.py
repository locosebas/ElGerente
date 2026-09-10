"""documentos — validación del enlace. Ver docs/features/documentos/spec.md §7."""
from __future__ import annotations

import pytest

from app.core.errors import DatosInvalidos
from app.documentos.enlace import validar_enlace


def test_validar_enlace_acepta_https():
    url = "  https://drive.google.com/file/d/abc/view  "
    assert validar_enlace(url) == "https://drive.google.com/file/d/abc/view"


@pytest.mark.parametrize("valor", [None, "", "   "])
def test_validar_enlace_vacio_es_none(valor):
    assert validar_enlace(valor) is None


@pytest.mark.parametrize("valor", ["drive.google.com/x", "ftp://x", "javascript:alert(1)"])
def test_validar_enlace_rechaza_no_url(valor):
    with pytest.raises(DatosInvalidos):
        validar_enlace(valor)


def test_validar_enlace_rechaza_muy_largo():
    with pytest.raises(DatosInvalidos):
        validar_enlace("https://x/" + "a" * 500)
