"""Modelo de `contrato` — registro informativo. Ver docs/features/contratos/spec.md."""
from __future__ import annotations

import enum
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class EstadoContrato(str, enum.Enum):
    VIGENTE = "vigente"
    TERMINADO = "terminado"


class Contrato(Base):
    __tablename__ = "contrato"

    id: Mapped[int] = mapped_column(primary_key=True)
    tercero_id: Mapped[int] = mapped_column(ForeignKey("tercero.id"), index=True)
    objeto: Mapped[str] = mapped_column(Text)
    valor: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    fecha_inicio: Mapped[date] = mapped_column(Date)
    fecha_fin: Mapped[date | None] = mapped_column(Date, nullable=True)
    estado: Mapped[EstadoContrato] = mapped_column(
        Enum(EstadoContrato), default=EstadoContrato.VIGENTE
    )
    # Enlace al PDF del contrato firmado (URL, típicamente de Drive).
    # Ver docs/features/documentos/spec.md.
    enlace_documento: Mapped[str | None] = mapped_column(String(500), nullable=True)
