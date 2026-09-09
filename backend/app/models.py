"""Agregador de modelos.

Importar este módulo registra TODAS las tablas del proyecto en
`Base.metadata`. Lo usan Alembic (para las migraciones) y los tests
(para crear el esquema en memoria). Cada feature define sus modelos en
su propio `models.py`; aquí solo se los reúne.
"""
from __future__ import annotations

from app.contabilidad.models import (  # noqa: F401
    Asiento,
    Cuenta,
    LineaAsiento,
)
from app.features.contratos.models import Contrato  # noqa: F401
from app.features.facturas.models import Factura  # noqa: F401
from app.features.terceros.models import Tercero  # noqa: F401

__all__ = ["Asiento", "Contrato", "Cuenta", "Factura", "LineaAsiento", "Tercero"]
