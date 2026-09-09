"""Lógica de pago/cobro de facturas. Ver docs/features/pagos/spec.md §3."""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.contabilidad import codigos
from app.contabilidad.asientos import crear_asiento, cuenta_requerida
from app.contabilidad.models import LibroContable, LineaAsiento, OrigenAsiento
from app.core.errors import Conflicto, DatosInvalidos
from app.features.facturas.models import EstadoFactura, Factura, TipoFactura
from app.features.facturas.service import obtener_factura

_CERO = Decimal("0")


async def pagar_factura(
    session: AsyncSession, *, factura_id: int, medio_pago: str, fecha: date
) -> Factura:
    factura = await obtener_factura(session, factura_id)  # 404 si no existe

    if factura.estado != EstadoFactura.PENDIENTE:
        raise Conflicto(
            f"La factura {factura_id} ya está en estado '{factura.estado.value}'"
        )
    if medio_pago not in codigos.MEDIOS_PAGO:
        raise DatosInvalidos(
            f"Medio de pago '{medio_pago}' inválido (usar 'caja' o 'bancos')"
        )

    caja_o_bancos = await cuenta_requerida(session, codigos.MEDIOS_PAGO[medio_pago])

    if factura.tipo == TipoFactura.RECIBIDA:
        cxp = await cuenta_requerida(session, codigos.CUENTAS_POR_PAGAR)
        lineas = [
            LineaAsiento(cuenta=cxp, debito=factura.total, credito=_CERO),
            LineaAsiento(cuenta=caja_o_bancos, debito=_CERO, credito=factura.total),
        ]
        descripcion = f"Pago factura recibida {factura.numero}"
    else:
        cxc = await cuenta_requerida(session, codigos.CUENTAS_POR_COBRAR)
        lineas = [
            LineaAsiento(cuenta=caja_o_bancos, debito=factura.total, credito=_CERO),
            LineaAsiento(cuenta=cxc, debito=_CERO, credito=factura.total),
        ]
        descripcion = f"Cobro factura emitida {factura.numero}"

    await crear_asiento(
        session,
        fecha=fecha,
        descripcion=descripcion,
        origen=OrigenAsiento.FACTURA,
        lineas=lineas,
        libro=LibroContable.OFICIAL,
        documento_soporte=descripcion,
    )

    factura.estado = EstadoFactura.PAGADA
    await session.commit()
    await session.refresh(factura)
    return factura
