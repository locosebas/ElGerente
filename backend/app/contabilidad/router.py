"""Endpoints de solo lectura del núcleo contable: /cuentas, /asientos, /balance."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.contabilidad.balance import calcular_balance
from app.contabilidad.models import Asiento, Cuenta, LibroContable
from app.contabilidad.schemas import AsientoOut, CuentaOut, SaldoCuenta
from app.core.db import get_db

router = APIRouter(tags=["contabilidad"])


def serializar_asiento(asiento: Asiento) -> dict:
    """AsientoOut necesita cuenta_codigo/cuenta_nombre por línea, que viven
    en la cuenta relacionada — por eso no se devuelve el objeto ORM tal cual.
    """
    return {
        "id": asiento.id,
        "fecha": asiento.fecha,
        "descripcion": asiento.descripcion,
        "origen": asiento.origen,
        "libro": asiento.libro,
        "documento_soporte": asiento.documento_soporte,
        "created_at": asiento.created_at,
        "lineas": [
            {
                "cuenta_codigo": linea.cuenta.codigo,
                "cuenta_nombre": linea.cuenta.nombre,
                "debito": linea.debito,
                "credito": linea.credito,
            }
            for linea in asiento.lineas
        ],
    }


@router.get("/cuentas", response_model=list[CuentaOut])
async def listar_cuentas(db: AsyncSession = Depends(get_db)) -> list[Cuenta]:
    return list(
        (await db.execute(select(Cuenta).order_by(Cuenta.codigo))).scalars().all()
    )


@router.get("/asientos", response_model=list[AsientoOut])
async def listar_asientos(
    libro: LibroContable | None = None, db: AsyncSession = Depends(get_db)
) -> list[dict]:
    stmt = select(Asiento).order_by(Asiento.id)
    if libro is not None:
        stmt = stmt.where(Asiento.libro == libro)
    asientos = (await db.execute(stmt)).scalars().all()
    return [serializar_asiento(a) for a in asientos]


@router.get("/balance", response_model=list[SaldoCuenta])
async def obtener_balance(
    incluir_interna: bool = False, db: AsyncSession = Depends(get_db)
) -> list[dict]:
    return await calcular_balance(db, incluir_interna=incluir_interna)
