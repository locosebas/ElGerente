"""Crea las tablas y siembra el plan de cuentas inicial.

Ejecutar una sola vez desde backend/: python -m app.seed
"""
from app.db import Base, SessionLocal, engine
from app.models import Cuenta, TipoCuenta

PLAN_DE_CUENTAS_INICIAL = [
    ("1105", "Caja", TipoCuenta.ACTIVO),
    ("1110", "Bancos", TipoCuenta.ACTIVO),
    ("1305", "Cuentas por cobrar", TipoCuenta.ACTIVO),
    ("2205", "Cuentas por pagar", TipoCuenta.PASIVO),
    ("2408", "Impuestos por pagar - IVA", TipoCuenta.PASIVO),
    ("3115", "Capital", TipoCuenta.PATRIMONIO),
    ("4135", "Ingresos por ventas", TipoCuenta.INGRESO),
    ("5195", "Gastos diversos", TipoCuenta.GASTO),
]


def seed() -> None:
    Base.metadata.create_all(engine)
    session = SessionLocal()
    try:
        if session.query(Cuenta).count() > 0:
            print("El plan de cuentas ya tiene datos, no se vuelve a sembrar.")
            return
        for codigo, nombre, tipo in PLAN_DE_CUENTAS_INICIAL:
            session.add(Cuenta(codigo=codigo, nombre=nombre, tipo=tipo))
        session.commit()
        print(f"Sembradas {len(PLAN_DE_CUENTAS_INICIAL)} cuentas.")
    finally:
        session.close()


if __name__ == "__main__":
    seed()
