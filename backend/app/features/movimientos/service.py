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
from app.core.logging import log
from app.features.terceros.service import obtener_tercero

_CERO = Decimal("0")
_log = log("movimientos")


async def registrar_movimiento_manual(
    session: AsyncSession,
    *,
    fecha: date,
    descripcion: str,
    libro: LibroContable,
    tercero_id: int,
    documento_soporte: str | None,
    lineas: list[dict],
) -> Asiento:
    tercero = await obtener_tercero(session, tercero_id)  # 404 si no existe

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
            tercero_id=tercero_id,
        )
    except AsientoDesbalanceado as exc:
        # En un movimiento manual, el descuadre es error del usuario (422),
        # no una falla del sistema (500).
        raise DatosInvalidos(str(exc)) from exc

    # Deja el tercero ya cargado en memoria para que el serializador de la
    # respuesta no dispare una carga perezosa (prohibida en async).
    asiento.tercero = tercero
    await session.commit()
    _log.info(
        "Movimiento manual registrado — asiento #%d libro=%s lineas=%d",
        asiento.id,
        libro.value,
        len(lineas_orm),
    )
    # No se hace refresh: `asiento` ya tiene sus líneas y cuentas cargadas en
    # memoria, y `expire_on_commit=False` las mantiene accesibles. Un refresh
    # expiraría las relaciones y forzaría una carga perezosa (que async prohíbe).
    return asiento
