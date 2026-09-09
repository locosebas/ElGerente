"""Conexión a la base de datos — SQLAlchemy 2.0 en modo asíncrono.

- `engine`: el motor async, construido a partir de `DATABASE_URL`.
- `SessionLocal`: fábrica de sesiones async.
- `Base`: clase madre de todos los modelos ORM.
- `get_db`: dependencia de FastAPI que entrega una sesión por petición y
  hace rollback si la petición falla.
- `verificar_conexion`: comprueba que la BD responde (para el arranque y
  el endpoint de salud).

Pasar de SQLite a PostgreSQL = cambiar `DATABASE_URL` en el .env. Nada de
este archivo ni de los modelos se toca.
"""
from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings
from app.core.logging import log

_log = log("db")


class Base(DeclarativeBase):
    """Todos los modelos heredan de aquí; `Base.metadata` conoce todas las tablas."""


_settings = get_settings()


def _opciones_engine(url: str) -> dict:
    """SQLite (archivo) no usa pool; PostgreSQL sí, y conviene reciclar
    conexiones y verificarlas antes de usarlas (`pool_pre_ping`) para
    aguantar cortes de red o reinicios del servidor de BD."""
    if url.startswith("sqlite"):
        return {}
    return {
        "pool_pre_ping": True,
        "pool_recycle": 1800,
        "pool_size": 5,
        "max_overflow": 10,
    }


engine = create_async_engine(
    _settings.database_url, future=True, **_opciones_engine(_settings.database_url)
)

SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Entrega una sesión por petición.

    - No hace commit automático: cada servicio decide cuándo confirmar.
    - Si la petición lanza una excepción, hace rollback antes de cerrar,
      para no dejar una transacción a medias abierta en el pool.
    """
    session = SessionLocal()
    try:
        yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def verificar_conexion() -> bool:
    """True si la base de datos responde a un `SELECT 1`."""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as exc:  # noqa: BLE001 — se quiere capturar cualquier fallo de conexión
        _log.error("La base de datos no responde: %s", exc)
        return False
