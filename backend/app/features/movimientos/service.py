"""Lógica de movimientos manuales (asientos oficiales con soporte / internos).

Ver docs/features/movimientos/spec.md §3.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.contabilidad.asientos import (
    AsientoDesbalanceado,
    crear_asiento,
    cuenta_por_codigo,
)
from app.contabilidad.models import Asiento, LibroContable, LineaAsiento, OrigenAsiento
from app.core.errors import DatosInvalidos, NoEncontrado

_CERO = Decimal("0")


async def registrar_movimiento_manual(
    session: AsyncSession,
    *,
    fecha: date,
    descripcion: str,
    libro: LibroContable,
    documento_soporte: str | None,
    lineas: list[dict],
) -> Asiento:
    if len(lineas) < 2:
        raise DatosInvalidos("Un asiento manual requiere al menos 2 líneas")

    lineas_orm: list[LineaAsiento] = []
    for linea in lineas:
        debito = Decimal(str(linea["debito"]))
        credito = Decimal(str(linea["credito"]))
        if debito == _CERO and credito == _CERO:
            raise DatosInvalidos(
                "Cada línea debe tener débito o crédito distinto de cero"
            )
        cuenta = await cuenta_por_codigo(session, linea["cuenta_codigo"])
        if cuenta is None:
            raise NoEncontrado(f"La cuenta '{linea['cuenta_codigo']}' no existe")
        lineas_orm.append(LineaAsiento(cuenta=cuenta, debito=debito, credito=credito))

    try:
        asiento = await crear_asiento(
            session,
            fecha=fecha,
            descripcion=descripcion,
            origen=OrigenAsiento.MANUAL,
            lineas=lineas_orm,
            libro=libro,
            documento_soporte=documento_soporte,
        )
    except AsientoDesbalanceado as exc:
        # En un movimiento manual, el descuadre es error del usuario (422),
        # no una falla del sistema (500).
        raise DatosInvalidos(str(exc)) from exc

    await session.commit()
    # No se hace refresh: `asiento` ya tiene sus líneas y cuentas cargadas en
    # memoria, y `expire_on_commit=False` las mantiene accesibles. Un refresh
    # expiraría las relaciones y forzaría una carga perezosa (que async prohíbe).
    return asiento
