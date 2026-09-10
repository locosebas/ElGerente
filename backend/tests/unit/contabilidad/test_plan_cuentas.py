"""contabilidad-nucleo / plan de cuentas — siembra idempotente."""
from __future__ import annotations

from sqlalchemy import func, select

from app.contabilidad.models import Cuenta
from app.contabilidad.plan_cuentas import sembrar_plan_de_cuentas


async def _contar(session) -> int:
    return (await session.execute(select(func.count()).select_from(Cuenta))).scalar_one()


async def test_seed_es_idempotente(db_session):
    # El fixture autouse `plan_cuentas` ya sembró una vez.
    assert await _contar(db_session) == 11
    insertadas = await sembrar_plan_de_cuentas(db_session)
    assert insertadas == 0
    assert await _contar(db_session) == 11
