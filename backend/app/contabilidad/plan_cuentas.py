"""Plan de cuentas inicial y su siembra idempotente.

Ver la tabla completa en docs/features/contabilidad-nucleo/spec.md §5.
Los códigos están inspirados en el PUC colombiano para no chocar con la
DIAN más adelante.
"""
from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.contabilidad.models import Cuenta, TipoCuenta

PLAN_DE_CUENTAS_INICIAL: list[tuple[str, str, TipoCuenta]] = [
    ("1105", "Caja", TipoCuenta.ACTIVO),
    ("1110", "Bancos", TipoCuenta.ACTIVO),
    ("1305", "Cuentas por cobrar", TipoCuenta.ACTIVO),
    ("2105", "Obligaciones financieras", TipoCuenta.PASIVO),
    ("2205", "Cuentas por pagar", TipoCuenta.PASIVO),
    ("2408", "Impuestos por pagar - IVA", TipoCuenta.PASIVO),
    ("2905", "Cuentas con el dueño", TipoCuenta.PASIVO),
    ("3115", "Capital", TipoCuenta.PATRIMONIO),
    ("4135", "Ingresos por ventas", TipoCuenta.INGRESO),
    ("5195", "Gastos diversos", TipoCuenta.GASTO),
    ("5905", "Gastos internos sin soporte", TipoCuenta.GASTO),
]


async def sembrar_plan_de_cuentas(session: AsyncSession) -> int:
    """Inserta el plan de cuentas si aún no hay cuentas. Idempotente:
    devuelve cuántas cuentas insertó (0 si ya estaba sembrado).
    """
    ya_hay = (await session.execute(select(func.count()).select_from(Cuenta))).scalar_one()
    if ya_hay:
        return 0
    session.add_all(
        Cuenta(codigo=codigo, nombre=nombre, tipo=tipo)
        for codigo, nombre, tipo in PLAN_DE_CUENTAS_INICIAL
    )
    await session.commit()
    return len(PLAN_DE_CUENTAS_INICIAL)
