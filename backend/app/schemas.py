"""Esquemas Pydantic — la forma de los datos que entran y salen por la API.

No confundir con app/models.py (esas son las tablas de la base de datos).
Estos esquemas son el "contrato" público de la API.
"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models import (
    EstadoContrato,
    EstadoFactura,
    LibroContable,
    OrigenAsiento,
    TipoCuenta,
    TipoFactura,
    TipoTercero,
)


class TerceroCreate(BaseModel):
    nombre: str
    nit_cedula: str
    tipo: TipoTercero


class TerceroOut(TerceroCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class LineaAsientoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    cuenta_codigo: str
    cuenta_nombre: str
    debito: Decimal
    credito: Decimal


class AsientoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    fecha: date
    descripcion: str
    origen: OrigenAsiento
    libro: LibroContable
    documento_soporte: str | None
    created_at: datetime
    lineas: list[LineaAsientoOut]


class LineaMovimientoIn(BaseModel):
    cuenta_codigo: str
    debito: Decimal = Decimal("0")
    credito: Decimal = Decimal("0")


class MovimientoManualCreate(BaseModel):
    fecha: date
    descripcion: str
    libro: LibroContable
    documento_soporte: str | None = None
    lineas: list[LineaMovimientoIn]


class FacturaCreate(BaseModel):
    tipo: TipoFactura
    numero: str
    fecha: date
    tercero_id: int
    subtotal: Decimal
    iva: Decimal = Decimal("0")


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


class PagarFacturaRequest(BaseModel):
    medio_pago: str  # "caja" o "bancos"
    fecha: date


class ContratoCreate(BaseModel):
    tercero_id: int
    objeto: str
    valor: Decimal
    fecha_inicio: date
    fecha_fin: date | None = None


class ContratoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    tercero_id: int
    objeto: str
    valor: Decimal
    fecha_inicio: date
    fecha_fin: date | None
    estado: EstadoContrato


class CuentaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    codigo: str
    nombre: str
    tipo: TipoCuenta


class SaldoCuenta(BaseModel):
    cuenta_codigo: str
    cuenta_nombre: str
    tipo: TipoCuenta
    saldo: Decimal
