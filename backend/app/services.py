"""Lógica de negocio del Módulo 1.

Todas las reglas de generación automática de asientos viven aquí, tal
como están documentadas en
analysis/02-architecture/modulo-1-api-design.md. Los routers de
app/main.py no deben tomar ninguna decisión contable por su cuenta —
solo llaman a estas funciones.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    Asiento,
    Contrato,
    Cuenta,
    EstadoFactura,
    Factura,
    LibroContable,
    LineaAsiento,
    OrigenAsiento,
    Tercero,
    TipoCuenta,
    TipoFactura,
)

CODIGO_CAJA = "1105"
CODIGO_BANCOS = "1110"
CODIGO_CUENTAS_POR_COBRAR = "1305"
CODIGO_CUENTAS_POR_PAGAR = "2205"
CODIGO_IVA = "2408"
CODIGO_INGRESOS_VENTAS = "4135"
CODIGO_GASTOS = "5195"

MEDIOS_PAGO_VALIDOS = {"caja": CODIGO_CAJA, "bancos": CODIGO_BANCOS}


class TerceroNoExisteError(Exception):
    pass


class FacturaNoExisteError(Exception):
    pass


class FacturaYaLiquidadaError(Exception):
    pass


class MedioPagoInvalidoError(Exception):
    pass


class DocumentoSoporteRequeridoError(Exception):
    """libro=oficial siempre exige documento_soporte (ver modulo-1-api-design.md, sección 3)."""


class CuentaNoExisteError(Exception):
    pass


class LineasInvalidasError(Exception):
    """Menos de 2 líneas, o alguna línea sin monto en débito ni crédito."""


class AsientoDesbalanceadoError(Exception):
    """No debería ocurrir nunca si las reglas de este archivo son correctas.

    Es una red de seguridad: si algún día una regla se edita mal, esto
    aborta la operación en vez de guardar contabilidad inconsistente.
    """


def _cuenta_por_codigo(session: Session, codigo: str) -> Cuenta:
    cuenta = session.execute(select(Cuenta).where(Cuenta.codigo == codigo)).scalar_one()
    return cuenta


def _crear_asiento(
    session: Session,
    fecha: date,
    descripcion: str,
    origen: OrigenAsiento,
    lineas: list[LineaAsiento],
    *,
    libro: LibroContable = LibroContable.OFICIAL,
    documento_soporte: str | None = None,
) -> Asiento:
    if libro == LibroContable.OFICIAL and not documento_soporte:
        raise DocumentoSoporteRequeridoError(
            "Un asiento de libro oficial siempre requiere documento_soporte"
        )
    asiento = Asiento(
        fecha=fecha,
        descripcion=descripcion,
        origen=origen,
        libro=libro,
        documento_soporte=documento_soporte,
        lineas=lineas,
    )
    if not asiento.cuadra():
        total_debito = sum((l.debito for l in lineas), Decimal("0"))
        total_credito = sum((l.credito for l in lineas), Decimal("0"))
        raise AsientoDesbalanceadoError(
            f"Asiento no cuadra: debito={total_debito} credito={total_credito}"
        )
    session.add(asiento)
    session.flush()
    return asiento


def registrar_factura(
    session: Session,
    *,
    tipo: TipoFactura,
    numero: str,
    fecha: date,
    tercero_id: int,
    subtotal: Decimal,
    iva: Decimal,
) -> Factura:
    tercero = session.get(Tercero, tercero_id)
    if tercero is None:
        raise TerceroNoExisteError(f"Tercero {tercero_id} no existe")

    total = subtotal + iva

    cuenta_gastos = _cuenta_por_codigo(session, CODIGO_GASTOS)
    cuenta_iva = _cuenta_por_codigo(session, CODIGO_IVA)
    cuenta_cxp = _cuenta_por_codigo(session, CODIGO_CUENTAS_POR_PAGAR)
    cuenta_cxc = _cuenta_por_codigo(session, CODIGO_CUENTAS_POR_COBRAR)
    cuenta_ingresos = _cuenta_por_codigo(session, CODIGO_INGRESOS_VENTAS)

    if tipo == TipoFactura.RECIBIDA:
        lineas = [
            LineaAsiento(cuenta=cuenta_gastos, debito=subtotal, credito=Decimal("0")),
            LineaAsiento(cuenta=cuenta_iva, debito=iva, credito=Decimal("0")),
            LineaAsiento(cuenta=cuenta_cxp, debito=Decimal("0"), credito=total),
        ]
        descripcion = f"Factura recibida {numero}"
    else:
        lineas = [
            LineaAsiento(cuenta=cuenta_cxc, debito=total, credito=Decimal("0")),
            LineaAsiento(cuenta=cuenta_ingresos, debito=Decimal("0"), credito=subtotal),
            LineaAsiento(cuenta=cuenta_iva, debito=Decimal("0"), credito=iva),
        ]
        descripcion = f"Factura emitida {numero}"

    asiento = _crear_asiento(
        session,
        fecha,
        descripcion,
        OrigenAsiento.FACTURA,
        lineas,
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
    session.commit()
    session.refresh(factura)
    return factura


def pagar_factura(
    session: Session, *, factura_id: int, medio_pago: str, fecha: date
) -> Factura:
    factura = session.get(Factura, factura_id)
    if factura is None:
        raise FacturaNoExisteError(f"Factura {factura_id} no existe")
    if factura.estado != EstadoFactura.PENDIENTE:
        raise FacturaYaLiquidadaError(
            f"Factura {factura_id} ya está en estado '{factura.estado.value}'"
        )
    if medio_pago not in MEDIOS_PAGO_VALIDOS:
        raise MedioPagoInvalidoError(f"Medio de pago '{medio_pago}' inválido")

    cuenta_caja_o_bancos = _cuenta_por_codigo(session, MEDIOS_PAGO_VALIDOS[medio_pago])

    if factura.tipo == TipoFactura.RECIBIDA:
        cuenta_cxp = _cuenta_por_codigo(session, CODIGO_CUENTAS_POR_PAGAR)
        lineas = [
            LineaAsiento(cuenta=cuenta_cxp, debito=factura.total, credito=Decimal("0")),
            LineaAsiento(
                cuenta=cuenta_caja_o_bancos, debito=Decimal("0"), credito=factura.total
            ),
        ]
        descripcion = f"Pago factura recibida {factura.numero}"
    else:
        cuenta_cxc = _cuenta_por_codigo(session, CODIGO_CUENTAS_POR_COBRAR)
        lineas = [
            LineaAsiento(
                cuenta=cuenta_caja_o_bancos, debito=factura.total, credito=Decimal("0")
            ),
            LineaAsiento(cuenta=cuenta_cxc, debito=Decimal("0"), credito=factura.total),
        ]
        descripcion = f"Cobro factura emitida {factura.numero}"

    _crear_asiento(
        session,
        fecha,
        descripcion,
        OrigenAsiento.FACTURA,
        lineas,
        libro=LibroContable.OFICIAL,
        documento_soporte=descripcion,
    )

    factura.estado = EstadoFactura.PAGADA
    session.commit()
    session.refresh(factura)
    return factura


def registrar_movimiento_manual(
    session: Session,
    *,
    fecha: date,
    descripcion: str,
    libro: LibroContable,
    documento_soporte: str | None,
    lineas: list[dict],
) -> Asiento:
    if len(lineas) < 2:
        raise LineasInvalidasError("Un asiento manual requiere al menos 2 líneas")

    lineas_orm: list[LineaAsiento] = []
    for linea in lineas:
        debito = linea["debito"]
        credito = linea["credito"]
        if debito == Decimal("0") and credito == Decimal("0"):
            raise LineasInvalidasError(
                "Cada línea debe tener débito o crédito distinto de cero"
            )
        cuenta = session.execute(
            select(Cuenta).where(Cuenta.codigo == linea["cuenta_codigo"])
        ).scalar_one_or_none()
        if cuenta is None:
            raise CuentaNoExisteError(f"Cuenta '{linea['cuenta_codigo']}' no existe")
        lineas_orm.append(LineaAsiento(cuenta=cuenta, debito=debito, credito=credito))

    asiento = _crear_asiento(
        session,
        fecha,
        descripcion,
        OrigenAsiento.MANUAL,
        lineas_orm,
        libro=libro,
        documento_soporte=documento_soporte,
    )
    session.commit()
    session.refresh(asiento)
    return asiento


def registrar_contrato(
    session: Session,
    *,
    tercero_id: int,
    objeto: str,
    valor: Decimal,
    fecha_inicio: date,
    fecha_fin: date | None,
) -> Contrato:
    tercero = session.get(Tercero, tercero_id)
    if tercero is None:
        raise TerceroNoExisteError(f"Tercero {tercero_id} no existe")

    contrato = Contrato(
        tercero_id=tercero_id,
        objeto=objeto,
        valor=valor,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
    )
    session.add(contrato)
    session.commit()
    session.refresh(contrato)
    return contrato


def calcular_balance(session: Session, *, incluir_interna: bool = False) -> list[dict]:
    cuentas = session.execute(select(Cuenta).order_by(Cuenta.codigo)).scalars().all()
    resultado = []
    for cuenta in cuentas:
        lineas = cuenta.lineas
        if not incluir_interna:
            lineas = [l for l in lineas if l.asiento.libro == LibroContable.OFICIAL]
        total_debito = sum((l.debito for l in lineas), Decimal("0"))
        total_credito = sum((l.credito for l in lineas), Decimal("0"))
        if cuenta.tipo in (TipoCuenta.ACTIVO, TipoCuenta.GASTO):
            saldo = total_debito - total_credito
        else:
            saldo = total_credito - total_debito
        resultado.append(
            {
                "cuenta_codigo": cuenta.codigo,
                "cuenta_nombre": cuenta.nombre,
                "tipo": cuenta.tipo,
                "saldo": saldo,
            }
        )
    return resultado
