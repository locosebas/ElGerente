from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.features.facturas.models import EstadoFactura, TipoFactura


class FacturaCreate(BaseModel):
    tipo: TipoFactura
    numero: str
    fecha: date
    tercero_id: int
    subtotal: Decimal = Field(ge=0)
    iva: Decimal = Field(default=Decimal("0"), ge=0)
    enlace_documento: str | None = None


class FacturaEnlace(BaseModel):
    """Cuerpo del PATCH: solo el enlace al PDF (puede ser null para quitarlo)."""

    enlace_documento: str | None


class FacturaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    tipo: TipoFactura
    numero: str
    fecha: date
    tercero_id: int
    subtotal: Decimal
    iva: Decimal
    total: Decimal
    estado: EstadoFactura
    asiento_id: int | None
    enlace_documento: str | None


class PagarFacturaRequest(BaseModel):
    medio_pago: str  # "caja" o "bancos"
    fecha: date
