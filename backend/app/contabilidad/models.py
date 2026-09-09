"""Modelos del núcleo contable — partida doble.

Ver docs/features/contabilidad-nucleo/spec.md §4 para el detalle de cada
campo y docs/aprendizaje/partida-doble.md para el porqué.
"""
from __future__ import annotations

import enum
from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class Naturaleza(str, enum.Enum):
    DEUDORA = "deudora"
    ACREEDORA = "acreedora"


class TipoCuenta(str, enum.Enum):
    ACTIVO = "activo"
    PASIVO = "pasivo"
    PATRIMONIO = "patrimonio"
    INGRESO = "ingreso"
    GASTO = "gasto"

    @property
    def naturaleza(self) -> Naturaleza:
        # Activo y Gasto aumentan por el débito; el resto por el crédito.
        if self in (TipoCuenta.ACTIVO, TipoCuenta.GASTO):
            return Naturaleza.DEUDORA
        return Naturaleza.ACREEDORA


class OrigenAsiento(str, enum.Enum):
    FACTURA = "factura"
    CONTRATO = "contrato"
    MANUAL = "manual"


class LibroContable(str, enum.Enum):
    OFICIAL = "oficial"
    INTERNA = "interna"


class Cuenta(Base):
    __tablename__ = "cuenta"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(10), unique=True, index=True)
    nombre: Mapped[str] = mapped_column(String(100))
    tipo: Mapped[TipoCuenta] = mapped_column(Enum(TipoCuenta))

    @property
    def naturaleza(self) -> Naturaleza:
        return self.tipo.naturaleza


class Asiento(Base):
    __tablename__ = "asiento"

    id: Mapped[int] = mapped_column(primary_key=True)
    fecha: Mapped[date] = mapped_column(Date)
    descripcion: Mapped[str] = mapped_column(Text)
    origen: Mapped[OrigenAsiento] = mapped_column(Enum(OrigenAsiento))
    libro: Mapped[LibroContable] = mapped_column(
        Enum(LibroContable), default=LibroContable.OFICIAL
    )
    documento_soporte: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None)
    )

    # lazy="selectin": las líneas se cargan siempre junto al asiento (con async
    # no se permite la carga perezosa "por sorpresa").
    lineas: Mapped[list[LineaAsiento]] = relationship(
        back_populates="asiento",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def cuadra(self) -> bool:
        """True si suma(débito) == suma(crédito) entre todas sus líneas.

        La regla central de la partida doble. Se valida en la capa de
        aplicación (no como constraint de BD) porque depende de sumar
        varias filas relacionadas.
        """
        total_debito = sum((linea.debito for linea in self.lineas), Decimal("0"))
        total_credito = sum((linea.credito for linea in self.lineas), Decimal("0"))
        return total_debito == total_credito


class LineaAsiento(Base):
    __tablename__ = "linea_asiento"

    id: Mapped[int] = mapped_column(primary_key=True)
    asiento_id: Mapped[int] = mapped_column(ForeignKey("asiento.id"), index=True)
    cuenta_id: Mapped[int] = mapped_column(ForeignKey("cuenta.id"), index=True)
    debito: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"))
    credito: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"))

    asiento: Mapped[Asiento] = relationship(back_populates="lineas")
    cuenta: Mapped[Cuenta] = relationship(lazy="selectin")
