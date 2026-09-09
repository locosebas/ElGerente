"""Modelo de `tercero` — clientes y proveedores. Ver docs/features/terceros/spec.md."""
from __future__ import annotations

import enum

from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class TipoTercero(str, enum.Enum):
    CLIENTE = "cliente"
    PROVEEDOR = "proveedor"


class Tercero(Base):
    __tablename__ = "tercero"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(150))
    nit_cedula: Mapped[str] = mapped_column(String(20))
    tipo: Mapped[TipoTercero] = mapped_column(Enum(TipoTercero))
