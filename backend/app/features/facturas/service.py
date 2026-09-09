"""Lógica de facturas: registrar factura emitida/recibida generando el
asiento automático. Ver docs/features/facturas/spec.md §3 (tablas de reglas).
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.contabilidad import codigos
from app.contabilidad.asientos import crear_asiento, cuenta_requerida
from app.contabilidad.models import LibroContable, LineaAsiento, OrigenAsiento
from app.core.errors import NoEncontrado
from app.features.facturas.models import EstadoFactura, Factura, TipoFactura
from app.features.terceros.service import obtener_tercero

_CERO = Decimal("0")


async def registrar_factura(
    session: AsyncSession,
    *,
    tipo: TipoFactura,
    numero: str,
    fecha: date,
    tercero_id: int,
    subtotal: Decimal,
    iva: Decimal = _CERO,
) -> Factura:
    await obtener_tercero(session, tercero_id)  # 404 si no existe

    total = subtotal + iva
    descripcion = (
        f"Factura recibida {numero}"
        if tipo == TipoFactura.RECIBIDA
        else f"Factura emitida {numero}"
    )

    gastos = await cuenta_requerida(session, codigos.GASTOS_DIVERSOS)
    cuenta_iva = await cuenta_requerida(session, codigos.IVA)
    cxp = await cuenta_requerida(session, codigos.CUENTAS_POR_PAGAR)
    cxc = await cuenta_requerida(session, codigos.CUENTAS_POR_COBRAR)
    ingresos = await cuenta_requerida(session, codigos.INGRESOS_VENTAS)

    if tipo == TipoFactura.RECIBIDA:
        lineas = [LineaAsiento(cuenta=gastos, debito=subtotal, credito=_CERO)]
        if iva != _CERO:
            lineas.append(LineaAsiento(cuenta=cuenta_iva, debito=iva, credito=_CERO))
        lineas.append(LineaAsiento(cuenta=cxp, debito=_CERO, credito=total))
    else:
        lineas = [LineaAsiento(cuenta=cxc, debito=total, credito=_CERO)]
        lineas.append(LineaAsiento(cuenta=ingresos, debito=_CERO, credito=subtotal))
        if iva != _CERO:
            lineas.append(LineaAsiento(cuenta=cuenta_iva, debito=_CERO, credito=iva))

    asiento = await crear_asiento(
        session,
        fecha=fecha,
        descripcion=descripcion,
        origen=OrigenAsiento.FACTURA,
        lineas=lineas,
        libro=LibroContable.OFICIAL,
        documento_soporte=descripcion,
    )

    factura = Factura(
        tipo=tipo,
        numero=numero,
        fecha=fecha,
        tercero_id=tercero_id,
        subtotal=subtotal,
        iva=iva,
        total=total,
        estado=EstadoFactura.PENDIENTE,
        asiento_id=asiento.id,
    )
    session.add(factura)
    await session.commit()
    await session.refresh(factura)
    return factura


async def obtener_factura(session: AsyncSession, factura_id: int) -> Factura:
    factura = await session.get(Factura, factura_id)
    if factura is None:
        raise NoEncontrado(f"Factura {factura_id} no existe")
    return factura


async def listar_facturas(
    session: AsyncSession,
    *,
    tipo: TipoFactura | None = None,
    estado: EstadoFactura | None = None,
) -> list[Factura]:
    stmt = select(Factura).order_by(Factura.id)
    if tipo is not None:
        stmt = stmt.where(Factura.tipo == tipo)
    if estado is not None:
        stmt = stmt.where(Factura.estado == estado)
    return list((await session.execute(stmt)).scalars().all())
