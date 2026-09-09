from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.features.contratos import service
from app.features.contratos.models import Contrato
from app.features.contratos.schemas import ContratoCreate, ContratoOut

router = APIRouter(prefix="/contratos", tags=["contratos"])


@router.post("", response_model=ContratoOut)
async def crear_contrato(
    data: ContratoCreate, db: AsyncSession = Depends(get_db)
) -> Contrato:
    return await service.registrar_contrato(db, **data.model_dump())


@router.get("", response_model=list[ContratoOut])
async def listar_contratos(db: AsyncSession = Depends(get_db)) -> list[Contrato]:
    return await service.listar_contratos(db)
