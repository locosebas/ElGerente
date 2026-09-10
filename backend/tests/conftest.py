"""Fixtures compartidas. Ver docs/arquitectura/testing.md.

Cada test corre contra una base SQLite EN MEMORIA nueva (no toca
elgerente.db ni Alembic). El esquema se levanta desde los modelos.
"""
from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401  (registra todas las tablas en Base.metadata)
from app.contabilidad.plan_cuentas import sembrar_plan_de_cuentas
from app.core.db import Base, get_db
from app.features.terceros.models import TipoTercero
from app.features.terceros.service import crear_tercero
from app.main import create_app


@pytest_asyncio.fixture
async def engine() -> AsyncGenerator:
    eng = create_async_engine(
        "sqlite+aiosqlite://",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture
async def session_factory(engine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)


@pytest_asyncio.fixture(autouse=True)
async def plan_cuentas(session_factory) -> None:
    """Siembra el plan de cuentas antes de cada test."""
    async with session_factory() as session:
        await sembrar_plan_de_cuentas(session)


@pytest_asyncio.fixture
async def db_session(session_factory) -> AsyncGenerator[AsyncSession, None]:
    """Sesión para los tests unitarios que llaman a los servicios directo."""
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def tercero_id(db_session) -> int:
    """Un tercero cualquiera, para los tests que necesitan un actor externo."""
    t = await crear_tercero(
        db_session, nombre="Actor Test", nit_cedula="1", tipo=TipoTercero.OTRO
    )
    return t.id


@pytest_asyncio.fixture
async def client(session_factory) -> AsyncGenerator[AsyncClient, None]:
    """Cliente HTTP contra la app real, con la base de datos de test enchufada."""
    app = create_app()

    async def _get_db_test() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = _get_db_test
    # raise_app_exceptions=False: los tests ven la respuesta HTTP real (incluido
    # un 500 con su cuerpo) como la vería un cliente, en vez de recibir la
    # excepción de Python.
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture
def fecha_hoy() -> str:
    return "2026-09-01"
