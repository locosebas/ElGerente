"""Esquemas de entrada/salida del núcleo contable (Pydantic)."""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.contabilidad.models import LibroContable, OrigenAsiento, TipoCuenta


class CuentaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    codigo: str
    nombre: str
    tipo: TipoCuenta


class LineaAsientoOut(BaseModel):
    cuenta_codigo: str
    cuenta_nombre: str
    debito: Decimal
    credito: Decimal


class AsientoOut(BaseModel):
    id: int
    fecha: date
    descripcion: str
    origen: OrigenAsiento
    libro: LibroContable
    documento_soporte: str | None
    created_at: datetime
    lineas: list[LineaAsientoOut]


class SaldoCuenta(BaseModel):
    cuenta_codigo: str
    cuenta_nombre: str
    tipo: TipoCuenta
    saldo: Decimal
