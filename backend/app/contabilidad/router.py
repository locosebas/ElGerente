"""Endpoints de solo lectura del núcleo contable.

/cuentas · /asientos · /balance · /cuentas/{codigo}/movimientos (extracto).
Ver docs/features/balance/spec.md.
"""
from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.contabilidad.balance import FiltroLibro, calcular_balance
from app.contabilidad.detalle_cuenta import movimientos_de_cuenta
from app.contabilidad.models import Asiento, Cuenta, LibroContable
from app.contabilidad.schemas import (
    AsientoOut,
    CuentaOut,
    DetalleCuentaOut,
    SaldoCuenta,
)
from app.contabilidad.serializers import serializar_asiento
from app.core.db import get_db

router = APIRouter(tags=["contabilidad"])


@router.get("/cuentas", response_model=list[CuentaOut])
async def listar_cuentas(db: AsyncSession = Depends(get_db)) -> list[Cuenta]:
    return list(
        (await db.execute(select(Cuenta).order_by(Cuenta.codigo))).scalars().all()
    )


@router.get("/asientos", response_model=list[AsientoOut])
async def listar_asientos(
    libro: LibroContable | None = None,
    desde: date | None = None,
    hasta: date | None = None,
    tercero_id: int | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    stmt = select(Asiento).order_by(Asiento.fecha, Asiento.id)
    if libro is not None:
        stmt = stmt.where(Asiento.libro == libro)
    if desde is not None:
        stmt = stmt.where(Asiento.fecha >= desde)
    if hasta is not None:
        stmt = stmt.where(Asiento.fecha <= hasta)
    if tercero_id is not None:
        stmt = stmt.where(Asiento.tercero_id == tercero_id)
    asientos = (await db.execute(stmt)).scalars().all()
    return [serializar_asiento(a) for a in asientos]


@router.get("/balance", response_model=list[SaldoCuenta])
async def obtener_balance(
    libro: FiltroLibro = FiltroLibro.OFICIAL,
    desde: date | None = None,
    hasta: date | None = None,
    tercero_id: int | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    return await calcular_balance(
        db, libro=libro, desde=desde, hasta=hasta, tercero_id=tercero_id
    )


@router.get("/cuentas/{codigo}/movimientos", response_model=DetalleCuentaOut)
async def detalle_de_cuenta(
    codigo: str,
    libro: FiltroLibro = FiltroLibro.OFICIAL,
    desde: date | None = None,
    hasta: date | None = None,
    tercero_id: int | None = None,
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await movimientos_de_cuenta(
        db, codigo, libro=libro, desde=desde, hasta=hasta, tercero_id=tercero_id
    )
