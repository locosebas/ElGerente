"""Validación de un enlace a documento.

Único punto que sabe qué es un "enlace de documento" válido. Ver
docs/features/documentos/spec.md §3 y §8 (plan para S3).
"""
from __future__ import annotations

from app.core.errors import DatosInvalidos

LARGO_MAXIMO = 500


def validar_enlace(valor: str | None) -> str | None:
    """Normaliza y valida un enlace opcional.

    - `None` / vacío / solo espacios  -> `None` (sin documento)
    - debe empezar por http:// o https://
    - máximo LARGO_MAXIMO caracteres
    """
    if valor is None:
        return None
    valor = valor.strip()
    if not valor:
        return None
    if not (valor.startswith("http://") or valor.startswith("https://")):
        raise DatosInvalidos("El enlace debe empezar por http:// o https://")
    if len(valor) > LARGO_MAXIMO:
        raise DatosInvalidos(f"El enlace no puede superar los {LARGO_MAXIMO} caracteres")
    return valor
