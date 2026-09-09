"""Modelo de `factura`. Ver docs/features/facturas/spec.md §4."""
from __future__ import annotations

import enum
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Enum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class TipoFactura(str, enum.Enum):
    EMITIDA = "emitida"
    RECIBIDA = "recibida"


class EstadoFactura(str, enum.Enum):
    PENDIENTE = "pendiente"
    PAGADA = "pagada"
    ANULADA = "anulada"


class Factura(Base):
    __tablename__ = "factura"

    id: Mapped[int] = mapped_column(primary_key=True)
    tipo: Mapped[TipoFactura] = mapped_column(Enum(TipoFactura))
    numero: Mapped[str] = mapped_column(String(50))
    fecha: Mapped[date] = mapped_column(Date)
    tercero_id: Mapped[int] = mapped_column(ForeignKey("tercero.id"), index=True)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    iva: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"))
    total: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    estado: Mapped[EstadoFactura] = mapped_column(
        Enum(EstadoFactura), default=EstadoFactura.PENDIENTE
    )
    asiento_id: Mapped[int | None] = mapped_column(
        ForeignKey("asiento.id"), nullable=True
    )
    archivo_original: Mapped[str | None] = mapped_column(String(255), nullable=True)
