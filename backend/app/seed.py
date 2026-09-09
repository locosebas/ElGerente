"""Siembra de datos base (plan de cuentas). NO crea tablas.

El esquema se crea con Alembic:  alembic upgrade head
Luego:                            python -m app.seed
"""
from __future__ import annotations

import asyncio

from app.contabilidad.plan_cuentas import sembrar_plan_de_cuentas
from app.core.db import SessionLocal


async def seed() -> None:
    async with SessionLocal() as session:
        insertadas = await sembrar_plan_de_cuentas(session)
    if insertadas:
        print(f"Sembradas {insertadas} cuentas.")
    else:
        print("El plan de cuentas ya tiene datos, no se vuelve a sembrar.")


if __name__ == "__main__":
    asyncio.run(seed())
