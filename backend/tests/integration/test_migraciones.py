"""El esquema de los modelos y el de las migraciones no deben separarse.

Corre `alembic upgrade head` sobre una base temporal y compara con
`Base.metadata`. Si alguien cambia un modelo y olvida generar la
migración, este test falla. Ver docs/arquitectura/base-de-datos.md.
"""
from __future__ import annotations

from pathlib import Path

from alembic.autogenerate import compare_metadata
from alembic.command import upgrade
from alembic.config import Config
from alembic.migration import MigrationContext
from sqlalchemy import create_engine

import app.models  # noqa: F401
from app.core.db import Base

BACKEND = Path(__file__).resolve().parents[2]


def test_no_hay_migracion_pendiente(tmp_path):
    db = tmp_path / "check.db"

    cfg = Config(str(BACKEND / "alembic.ini"))
    cfg.set_main_option("script_location", str(BACKEND / "alembic"))
    cfg.set_main_option("sqlalchemy.url", f"sqlite+aiosqlite:///{db}")
    upgrade(cfg, "head")

    engine = create_engine(f"sqlite:///{db}")
    with engine.connect() as conn:
        ctx = MigrationContext.configure(conn)
        diferencias = compare_metadata(ctx, Base.metadata)
    engine.dispose()

    assert diferencias == [], f"Faltan migraciones para: {diferencias}"
