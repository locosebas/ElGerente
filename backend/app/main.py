"""API del Módulo 1. Los endpoints solo traducen HTTP <-> services.

Ver analysis/02-architecture/modulo-1-api-design.md para el diseño
completo (reglas de negocio, tabla de endpoints, manejo de errores).
"""
from __future__ import annotations

from collections.abc import Generator

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import services
from app.db import SessionLocal
from app.models import Asiento, Contrato, Cuenta, Factura, Tercero
from app.schemas import (
    AsientoOut,
    ContratoCreate,
    ContratoOut,
    CuentaOut,
    FacturaCreate,
    FacturaOut,
    MovimientoManualCreate,
    PagarFacturaRequest,
    SaldoCuenta,
    TerceroCreate,
    TerceroOut,
)

app = FastAPI(title="El Gerente — Módulo 1: Motor Contable")


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _serializar_asiento(a: Asiento) -> dict:
    """AsientoOut necesita cuenta_codigo/cuenta_nombre por línea, que no son
    atributos directos de LineaAsiento (viven en la cuenta relacionada) — por
    eso no se puede devolver el objeto ORM tal cual con response_model."""
    return {
        "id": a.id,
        "fecha": a.fecha,
        "descripcion": a.descripcion,
        "origen": a.origen,
        "libro": a.libro,
        "documento_soporte": a.documento_soporte,
        "created_at": a.created_at,
        "lineas": [
            {
                "cuenta_codigo": l.cuenta.codigo,
                "cuenta_nombre": l.cuenta.nombre,
                "debito": l.debito,
                "credito": l.credito,
            }
            for l in a.lineas
        ],
    }


@app.post("/terceros", response_model=TerceroOut)
def crear_tercero(data: TerceroCreate, db: Session = Depends(get_db)) -> Tercero:
    tercero = Tercero(**data.model_dump())
    db.add(tercero)
    db.commit()
    db.refresh(tercero)
    return tercero


@app.get("/terceros", response_model=list[TerceroOut])
def listar_terceros(db: Session = Depends(get_db)) -> list[Tercero]:
    return db.execute(select(Tercero)).scalars().all()


@app.post("/facturas", response_model=FacturaOut)
def crear_factura(data: FacturaCreate, db: Session = Depends(get_db)) -> Factura:
    try:
        return services.registrar_factura(db, **data.model_dump())
    except services.TerceroNoExisteError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except services.AsientoDesbalanceadoError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/facturas", response_model=list[FacturaOut])
def listar_facturas(
    tipo: str | None = None, estado: str | None = None, db: Session = Depends(get_db)
) -> list[Factura]:
    stmt = select(Factura)
    if tipo is not None:
        stmt = stmt.where(Factura.tipo == tipo)
    if estado is not None:
        stmt = stmt.where(Factura.estado == estado)
    return db.execute(stmt).scalars().all()


@app.get("/facturas/{factura_id}", response_model=FacturaOut)
def obtener_factura(factura_id: int, db: Session = Depends(get_db)) -> Factura:
    factura = db.get(Factura, factura_id)
    if factura is None:
        raise HTTPException(status_code=404, detail="Factura no existe")
    return factura


@app.post("/facturas/{factura_id}/pagar", response_model=FacturaOut)
def pagar_factura(
    factura_id: int, data: PagarFacturaRequest, db: Session = Depends(get_db)
) -> Factura:
    try:
        return services.pagar_factura(
            db, factura_id=factura_id, medio_pago=data.medio_pago, fecha=data.fecha
        )
    except services.FacturaNoExisteError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except services.FacturaYaLiquidadaError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    except services.MedioPagoInvalidoError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except services.AsientoDesbalanceadoError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/contratos", response_model=ContratoOut)
def crear_contrato(data: ContratoCreate, db: Session = Depends(get_db)) -> Contrato:
    try:
        return services.registrar_contrato(db, **data.model_dump())
    except services.TerceroNoExisteError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@app.get("/contratos", response_model=list[ContratoOut])
def listar_contratos(db: Session = Depends(get_db)) -> list[Contrato]:
    return db.execute(select(Contrato)).scalars().all()


@app.get("/cuentas", response_model=list[CuentaOut])
def listar_cuentas(db: Session = Depends(get_db)) -> list[Cuenta]:
    return db.execute(select(Cuenta).order_by(Cuenta.codigo)).scalars().all()


@app.get("/balance", response_model=list[SaldoCuenta])
def obtener_balance(
    incluir_interna: bool = False, db: Session = Depends(get_db)
) -> list[dict]:
    return services.calcular_balance(db, incluir_interna=incluir_interna)


@app.post("/movimientos", response_model=AsientoOut)
def crear_movimiento_manual(
    data: MovimientoManualCreate, db: Session = Depends(get_db)
) -> dict:
    try:
        asiento = services.registrar_movimiento_manual(
            db,
            fecha=data.fecha,
            descripcion=data.descripcion,
            libro=data.libro,
            documento_soporte=data.documento_soporte,
            lineas=[l.model_dump() for l in data.lineas],
        )
        return _serializar_asiento(asiento)
    except services.DocumentoSoporteRequeridoError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except services.LineasInvalidasError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except services.CuentaNoExisteError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except services.AsientoDesbalanceadoError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e


@app.get("/asientos", response_model=list[AsientoOut])
def listar_asientos(libro: str | None = None, db: Session = Depends(get_db)) -> list[dict]:
    stmt = select(Asiento).order_by(Asiento.id)
    if libro is not None:
        stmt = stmt.where(Asiento.libro == libro)
    asientos = db.execute(stmt).scalars().all()
    return [_serializar_asiento(a) for a in asientos]
