"""Errores de dominio y su traducción a respuestas HTTP.

Los servicios lanzan subclases de `DomainError` (no saben nada de HTTP).
Cada router traduce esas excepciones a `HTTPException` con
`http_para(exc)`, usando el `status_code` que la propia excepción declara.
"""
from __future__ import annotations

from fastapi import HTTPException


class DomainError(Exception):
    """Base de todos los errores de negocio. `status_code` es el HTTP sugerido."""

    status_code: int = 400

    def __init__(self, mensaje: str) -> None:
        super().__init__(mensaje)
        self.mensaje = mensaje


class NoEncontrado(DomainError):
    status_code = 404


class Conflicto(DomainError):
    status_code = 409


class DatosInvalidos(DomainError):
    status_code = 422


def http_para(exc: DomainError) -> HTTPException:
    return HTTPException(status_code=exc.status_code, detail=exc.mensaje)
