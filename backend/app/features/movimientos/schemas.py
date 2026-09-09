from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field

from app.contabilidad.models import LibroContable


class LineaMovimientoIn(BaseModel):
    cuenta_codigo: str
    debito: Decimal = Field(default=Decimal("0"), ge=0)
    credito: Decimal = Field(default=Decimal("0"), ge=0)


class MovimientoManualCreate(BaseModel):
    fecha: date
    descripcion: str
    libro: LibroContable
    documento_soporte: str | None = None
    lineas: list[LineaMovimientoIn]
