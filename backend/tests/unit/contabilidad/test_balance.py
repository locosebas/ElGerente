"""contabilidad-nucleo / balance — calcular_balance. Ver specs §7."""
from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from app.contabilidad.asientos import crear_asiento, cuenta_requerida
from app.contabilidad.balance import FiltroLibro, calcular_balance
from app.contabilidad.models import LibroContable, LineaAsiento, OrigenAsiento
from app.core.errors import DatosInvalidos

HOY = date(2026, 9, 1)


async def _linea(session, codigo, debito="0", credito="0") -> LineaAsiento:
    cuenta = await cuenta_requerida(session, codigo)
    return LineaAsiento(cuenta=cuenta, debito=Decimal(debito), credito=Decimal(credito))


async def _par(session, cta_debito, cta_credito, monto) -> list[LineaAsiento]:
    return [
        await _linea(session, cta_debito, debito=monto),
        await _linea(session, cta_credito, credito=monto),
    ]


def _saldo(balance: list[dict], codigo: str) -> Decimal:
    return next(fila["saldo"] for fila in balance if fila["cuenta_codigo"] == codigo)


async def test_balance_signo_por_naturaleza(db_session):
    # Activo (deudora): más débito -> saldo positivo.
    # Pasivo (acreedora): más crédito -> saldo positivo.
    await crear_asiento(
        db_session,
        fecha=HOY,
        descripcion="aporte",
        origen=OrigenAsiento.MANUAL,
        lineas=[
            await _linea(db_session, "1105", debito="1000"),  # Caja (activo)
            await _linea(db_session, "3115", credito="1000"),  # Capital (patrimonio)
        ],
        libro=LibroContable.OFICIAL,
        documento_soporte="aporte inicial",
    )
    await db_session.commit()

    balance = await calcular_balance(db_session)
    assert _saldo(balance, "1105") == Decimal("1000.00")
    assert _saldo(balance, "3115") == Decimal("1000.00")


async def test_balance_incluye_cuentas_sin_movimiento(db_session):
    balance = await calcular_balance(db_session)
    codigos = {fila["cuenta_codigo"] for fila in balance}
    assert len(balance) == 11
    assert "2408" in codigos
    assert all(fila["saldo"] == Decimal("0.00") or fila["saldo"] == 0 for fila in balance)


async def _asiento(session, descripcion, lineas, libro, fecha=HOY, soporte="x"):
    await crear_asiento(
        session,
        fecha=fecha,
        descripcion=descripcion,
        origen=OrigenAsiento.MANUAL,
        lineas=lineas,
        libro=libro,
        documento_soporte=soporte if libro is LibroContable.OFICIAL else None,
    )
    await session.commit()


async def test_balance_libro_oficial_interna_todos(db_session):
    await _asiento(
        db_session, "gasto oficial", await _par(db_session, "5195", "1105", "100"),
        LibroContable.OFICIAL,
    )
    await _asiento(
        db_session, "retiro informal", await _par(db_session, "2905", "1105", "50"),
        LibroContable.INTERNA,
    )

    oficial = await calcular_balance(db_session, libro=FiltroLibro.OFICIAL)
    interna = await calcular_balance(db_session, libro=FiltroLibro.INTERNA)
    total = await calcular_balance(db_session, libro=FiltroLibro.TODOS)

    assert _saldo(oficial, "1105") == Decimal("-100.00")
    assert _saldo(interna, "1105") == Decimal("-50.00")
    assert _saldo(total, "1105") == Decimal("-150.00")
    assert _saldo(oficial, "2905") == Decimal("0.00")
    assert _saldo(interna, "2905") == Decimal("-50.00")


async def test_balance_filtra_por_periodo(db_session):
    await _asiento(
        db_session, "junio", await _par(db_session, "5195", "1105", "10"),
        LibroContable.OFICIAL, fecha=date(2026, 6, 15),
    )
    await _asiento(
        db_session, "julio", await _par(db_session, "5195", "1105", "20"),
        LibroContable.OFICIAL, fecha=date(2026, 7, 15),
    )

    solo_junio = await calcular_balance(
        db_session, desde=date(2026, 6, 1), hasta=date(2026, 6, 30)
    )
    assert _saldo(solo_junio, "5195") == Decimal("10.00")

    todo = await calcular_balance(db_session)
    assert _saldo(todo, "5195") == Decimal("30.00")


async def test_balance_desde_mayor_que_hasta(db_session):
    with pytest.raises(DatosInvalidos):
        await calcular_balance(
            db_session, desde=date(2026, 7, 1), hasta=date(2026, 6, 1)
        )
