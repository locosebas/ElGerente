"""contabilidad-nucleo / balance — calcular_balance. Ver specs §7."""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from app.contabilidad.asientos import crear_asiento, cuenta_requerida
from app.contabilidad.balance import calcular_balance
from app.contabilidad.models import LibroContable, LineaAsiento, OrigenAsiento

HOY = date(2026, 9, 1)


async def _linea(session, codigo, debito="0", credito="0") -> LineaAsiento:
    cuenta = await cuenta_requerida(session, codigo)
    return LineaAsiento(cuenta=cuenta, debito=Decimal(debito), credito=Decimal(credito))


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
    assert len(balance) == 10
    assert "2408" in codigos
    assert all(fila["saldo"] == Decimal("0.00") or fila["saldo"] == 0 for fila in balance)


async def test_balance_ignora_interna_por_defecto(db_session):
    await crear_asiento(
        db_session,
        fecha=HOY,
        descripcion="retiro informal",
        origen=OrigenAsiento.MANUAL,
        lineas=[
            await _linea(db_session, "2905", debito="50"),
            await _linea(db_session, "1105", credito="50"),
        ],
        libro=LibroContable.INTERNA,
    )
    await db_session.commit()

    oficial = await calcular_balance(db_session)
    assert _saldo(oficial, "1105") == 0 or _saldo(oficial, "1105") == Decimal("0.00")

    total = await calcular_balance(db_session, incluir_interna=True)
    assert _saldo(total, "1105") == Decimal("-50.00")
    assert _saldo(total, "2905") == Decimal("-50.00")
