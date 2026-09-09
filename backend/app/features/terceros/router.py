from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.features.terceros import service
from app.features.terceros.models import Tercero, TipoTercero
from app.features.terceros.schemas import TerceroCreate, TerceroOut

router = APIRouter(prefix="/terceros", tags=["terceros"])


@router.post("", response_model=TerceroOut)
async def crear_tercero(data: TerceroCreate, db: AsyncSession = Depends(get_db)) -> Tercero:
    return await service.crear_tercero(db, **data.model_dump())


@router.get("", response_model=list[TerceroOut])
async def listar_terceros(
    tipo: TipoTercero | None = None, db: AsyncSession = Depends(get_db)
) -> list[Tercero]:
    return await service.listar_terceros(db, tipo=tipo)
