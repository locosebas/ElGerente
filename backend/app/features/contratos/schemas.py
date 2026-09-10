from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.features.contratos.models import EstadoContrato


class ContratoCreate(BaseModel):
    tercero_id: int
    objeto: str
    valor: Decimal = Field(ge=0)
    fecha_inicio: date
    fecha_fin: date | None = None
    enlace_documento: str | None = None


class ContratoEnlace(BaseModel):
    """Cuerpo del PATCH: solo el enlace al PDF (puede ser null para quitarlo)."""

    enlace_documento: str | None


class ContratoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    tercero_id: int
    objeto: str
    valor: Decimal
    fecha_inicio: date
    fecha_fin: date | None
    estado: EstadoContrato
    enlace_documento: str | None
