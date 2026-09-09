from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.features.facturas import service
from app.features.facturas.models import EstadoFactura, Factura, TipoFactura
from app.features.facturas.schemas import FacturaCreate, FacturaOut, PagarFacturaRequest
from app.features.pagos import service as pagos_service

router = APIRouter(prefix="/facturas", tags=["facturas"])


@router.post("", response_model=FacturaOut)
async def crear_factura(data: FacturaCreate, db: AsyncSession = Depends(get_db)) -> Factura:
    return await service.registrar_factura(db, **data.model_dump())


@router.get("", response_model=list[FacturaOut])
async def listar_facturas(
    tipo: TipoFactura | None = None,
    estado: EstadoFactura | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[Factura]:
    return await service.listar_facturas(db, tipo=tipo, estado=estado)


@router.get("/{factura_id}", response_model=FacturaOut)
async def obtener_factura(factura_id: int, db: AsyncSession = Depends(get_db)) -> Factura:
    return await service.obtener_factura(db, factura_id)


@router.post("/{factura_id}/pagar", response_model=FacturaOut)
async def pagar_factura(
    factura_id: int, data: PagarFacturaRequest, db: AsyncSession = Depends(get_db)
) -> Factura:
    return await pagos_service.pagar_factura(
        db, factura_id=factura_id, medio_pago=data.medio_pago, fecha=data.fecha
    )
