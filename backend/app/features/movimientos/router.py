from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.contabilidad.schemas import AsientoOut
from app.contabilidad.serializers import serializar_asiento
from app.core.db import get_db
from app.features.movimientos import service
from app.features.movimientos.schemas import MovimientoManualCreate

router = APIRouter(prefix="/movimientos", tags=["movimientos"])


@router.post("", response_model=AsientoOut)
async def crear_movimiento_manual(
    data: MovimientoManualCreate, db: AsyncSession = Depends(get_db)
) -> dict:
    asiento = await service.registrar_movimiento_manual(
        db,
        fecha=data.fecha,
        descripcion=data.descripcion,
        libro=data.libro,
        tercero_id=data.tercero_id,
        documento_soporte=data.documento_soporte,
        lineas=[linea.model_dump() for linea in data.lineas],
    )
    return serializar_asiento(asiento)
