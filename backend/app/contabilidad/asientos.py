"""`crear_asiento` — el único punto de escritura contable.

Toda feature que necesite registrar un hecho económico llama aquí. La
función valida el documento de soporte (si el libro es oficial) y el
cuadre de partida doble ANTES de guardar. Ver
docs/features/contabilidad-nucleo/spec.md §3 y §5.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.contabilidad.models import (
    Asiento,
    Cuenta,
    LibroContable,
    LineaAsiento,
    OrigenAsiento,
)
from app.core.errors import DatosInvalidos, DomainError
from app.core.logging import log

_log = log("contabilidad")


class DocumentoSoporteRequerido(DatosInvalidos):
    """Un asiento de libro oficial siempre exige documento_soporte."""


class AsientoDesbalanceado(DomainError):
    """La suma de débitos no iguala la de créditos.

    No debería ocurrir nunca si las reglas de las features son correctas;
    es una red de seguridad: aborta la operación en vez de guardar
    contabilidad inconsistente.
    """

    status_code = 500


class CuentaInexistente(DomainError):
    """Se pidió una cuenta que no está en el plan de cuentas."""

    status_code = 500


async def cuenta_por_codigo(session: AsyncSession, codigo: str) -> Cuenta | None:
    return (
        await session.execute(select(Cuenta).where(Cuenta.codigo == codigo))
    ).scalar_one_or_none()


async def cuenta_requerida(session: AsyncSession, codigo: str) -> Cuenta:
    """Como `cuenta_por_codigo` pero exige que exista (para las reglas
    automáticas, que usan cuentas del plan sembrado)."""
    cuenta = await cuenta_por_codigo(session, codigo)
    if cuenta is None:
        raise CuentaInexistente(
            f"La cuenta '{codigo}' no está en el plan de cuentas (¿falta sembrar?)"
        )
    return cuenta


async def crear_asiento(
    session: AsyncSession,
    *,
    fecha: date,
    descripcion: str,
    origen: OrigenAsiento,
    lineas: list[LineaAsiento],
    libro: LibroContable = LibroContable.OFICIAL,
    documento_soporte: str | None = None,
    tercero_id: int | None = None,
) -> Asiento:
    """Crea y valida un asiento. Hace `flush` (deja el id disponible),
    NO `commit` — quien llama decide cuándo confirmar la transacción.

    `tercero_id` es con qué actor externo se hizo la transacción; lo pasa la
    feature (la validación de que exista es responsabilidad de la feature).
    """
    if libro == LibroContable.OFICIAL and not (documento_soporte or "").strip():
        raise DocumentoSoporteRequerido(
            "Un asiento de libro oficial siempre requiere documento_soporte"
        )

    asiento = Asiento(
        fecha=fecha,
        descripcion=descripcion,
        origen=origen,
        libro=libro,
        documento_soporte=documento_soporte if libro == LibroContable.OFICIAL else None,
        tercero_id=tercero_id,
        lineas=lineas,
    )

    if not asiento.cuadra():
        total_debito = sum((linea.debito for linea in lineas), Decimal("0"))
        total_credito = sum((linea.credito for linea in lineas), Decimal("0"))
        _log.error(
            "Asiento descuadrado rechazado — origen=%s debito=%s credito=%s",
            origen.value,
            total_debito,
            total_credito,
        )
        raise AsientoDesbalanceado(
            f"Asiento no cuadra: debito={total_debito} credito={total_credito}"
        )

    session.add(asiento)
    await session.flush()
    _log.info(
        "Asiento #%d creado — origen=%s libro=%s lineas=%d",
        asiento.id,
        origen.value,
        libro.value,
        len(lineas),
    )
    return asiento
