from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from app.features.terceros.models import TipoTercero


class TerceroCreate(BaseModel):
    nombre: str
    nit_cedula: str
    tipo: TipoTercero


class TerceroOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre: str
    nit_cedula: str
    tipo: TipoTercero
