"""Modelos de datos del Módulo 1 — motor contable con partida doble.

Ver analysis/04-data-model/modulo-1-modelo-datos.md para el diseño
completo y el porqué de cada tabla.
"""
from __future__ import annotations

import enum
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class TipoCuenta(str, enum.Enum):
    ACTIVO = "activo"
    PASIVO = "pasivo"
    PATRIMONIO = "patrimonio"
    INGRESO = "ingreso"
    GASTO = "gasto"


class OrigenAsiento(str, enum.Enum):
    FACTURA = "factura"
    CONTRATO = "contrato"
    MANUAL = "manual"


class TipoTercero(str, enum.Enum):
    CLIENTE = "cliente"
    PROVEEDOR = "proveedor"


class TipoFactura(str, enum.Enum):
    EMITIDA = "emitida"
    RECIBIDA = "recibida"


class EstadoFactura(str, enum.Enum):
    PENDIENTE = "pendiente"
    PAGADA = "pagada"
    ANULADA = "anulada"


class EstadoContrato(str, enum.Enum):
    VIGENTE = "vigente"
    TERMINADO = "terminado"


class Cuenta(Base):
    __tablename__ = "cuenta"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(10), unique=True)
    nombre: Mapped[str] = mapped_column(String(100))
    tipo: Mapped[TipoCuenta] = mapped_column(Enum(TipoCuenta))

    lineas: Mapped[list["LineaAsiento"]] = relationship(back_populates="cuenta")


class Tercero(Base):
    __tablename__ = "tercero"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(150))
    nit_cedula: Mapped[str] = mapped_column(String(20))
    tipo: Mapped[TipoTercero] = mapped_column(Enum(TipoTercero))


class Asiento(Base):
    __tablename__ = "asiento"

    id: Mapped[int] = mapped_column(primary_key=True)
    fecha: Mapped[date] = mapped_column(Date)
    descripcion: Mapped[str] = mapped_column(Text)
    origen: Mapped[OrigenAsiento] = mapped_column(Enum(OrigenAsiento))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    lineas: Mapped[list["LineaAsiento"]] = relationship(
        back_populates="asiento", cascade="all, delete-orphan"
    )

    def cuadra(self) -> bool:
        """True si suma(débito) == suma(crédito) entre todas sus líneas.

        Esta es la regla central de la partida doble: se valida en la capa
        de aplicación (no como constraint de base de datos) porque depende
        de sumar varias filas relacionadas, algo que SQLite no valida solo.
        """
        total_debito = sum((l.debito for l in self.lineas), Decimal("0"))
        total_credito = sum((l.credito for l in self.lineas), Decimal("0"))
        return total_debito == total_credito


class LineaAsiento(Base):
    __tablename__ = "linea_asiento"

    id: Mapped[int] = mapped_column(primary_key=True)
    asiento_id: Mapped[int] = mapped_column(ForeignKey("asiento.id"))
    cuenta_id: Mapped[int] = mapped_column(ForeignKey("cuenta.id"))
    debito: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"))
    credito: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"))

    asiento: Mapped["Asiento"] = relationship(back_populates="lineas")
    cuenta: Mapped["Cuenta"] = relationship(back_populates="lineas")


class Factura(Base):
    __tablename__ = "factura"

    id: Mapped[int] = mapped_column(primary_key=True)
    tipo: Mapped[TipoFactura] = mapped_column(Enum(TipoFactura))
    numero: Mapped[str] = mapped_column(String(50))
    fecha: Mapped[date] = mapped_column(Date)
    tercero_id: Mapped[int] = mapped_column(ForeignKey("tercero.id"))
    subtotal: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    iva: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0"))
    total: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    estado: Mapped[EstadoFactura] = mapped_column(
        Enum(EstadoFactura), default=EstadoFactura.PENDIENTE
    )
    asiento_id: Mapped[int | None] = mapped_column(ForeignKey("asiento.id"), nullable=True)
    archivo_original: Mapped[str | None] = mapped_column(String(255), nullable=True)

    tercero: Mapped["Tercero"] = relationship()
    asiento: Mapped["Asiento | None"] = relationship()


class Contrato(Base):
    __tablename__ = "contrato"

    id: Mapped[int] = mapped_column(primary_key=True)
    tercero_id: Mapped[int] = mapped_column(ForeignKey("tercero.id"))
    objeto: Mapped[str] = mapped_column(Text)
    valor: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    fecha_inicio: Mapped[date] = mapped_column(Date)
    fecha_fin: Mapped[date | None] = mapped_column(Date, nullable=True)
    estado: Mapped[EstadoContrato] = mapped_column(
        Enum(EstadoContrato), default=EstadoContrato.VIGENTE
    )
    archivo_original: Mapped[str | None] = mapped_column(String(255), nullable=True)

    tercero: Mapped["Tercero"] = relationship()
