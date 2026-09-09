"""Ensamblado de la aplicación FastAPI.

`create_app()`:
- configura el logging,
- registra el ciclo de vida (chequeo de la base de datos al arrancar),
- monta el middleware que registra cada petición,
- registra los manejadores de errores (dominio, validación e inesperados),
- monta los routers de features y la interfaz gráfica.

Ver docs/arquitectura/vision-tecnica.md y docs/arquitectura/resiliencia-y-logs.md.
"""
from __future__ import annotations

import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func, select

# Registra todas las tablas en Base.metadata.
import app.models  # noqa: F401
from app.contabilidad.models import Cuenta
from app.contabilidad.router import router as contabilidad_router
from app.core.config import get_settings
from app.core.db import SessionLocal, engine, verificar_conexion
from app.core.errors import DomainError
from app.core.logging import configurar_logging, log
from app.features.contratos.router import router as contratos_router
from app.features.facturas.router import router as facturas_router
from app.features.movimientos.router import router as movimientos_router
from app.features.terceros.router import router as terceros_router

_WEB = Path(__file__).parent / "web"
_log = log("http")


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    ajustes = get_settings()
    arranque = log("arranque")
    arranque.info(
        "El Gerente arrancando — entorno=%s  base_de_datos=%s",
        ajustes.entorno,
        ajustes.database_url_sin_credenciales,
    )

    if await verificar_conexion():
        arranque.info("Conexión a la base de datos: OK")
        async with SessionLocal() as session:
            cuentas = (
                await session.execute(select(func.count()).select_from(Cuenta))
            ).scalar_one()
        if cuentas == 0:
            arranque.warning(
                "El plan de cuentas está vacío. Correr:  python -m app.seed"
            )
        else:
            arranque.info("Plan de cuentas: %d cuentas", cuentas)
    else:
        arranque.error(
            "La base de datos NO responde. La app arranca igual, pero las "
            "operaciones fallarán hasta que vuelva."
        )

    yield

    await engine.dispose()
    arranque.info("El Gerente detenido")


def create_app() -> FastAPI:
    ajustes = get_settings()
    configurar_logging(ajustes.log_level)

    app = FastAPI(
        title="El Gerente — Motor Contable",
        lifespan=lifespan,
        docs_url="/docs",
    )

    # --- Middleware: una línea de log por petición -------------------------
    @app.middleware("http")
    async def _registrar_peticion(request: Request, call_next):
        inicio = time.perf_counter()
        try:
            respuesta = await call_next(request)
        except Exception:
            ms = (time.perf_counter() - inicio) * 1000
            _log.exception(
                "%s %s -> excepción sin manejar (%.0f ms)",
                request.method,
                request.url.path,
                ms,
            )
            raise
        ms = (time.perf_counter() - inicio) * 1000
        ruta = request.url.path
        ruidosa = ruta in ("/salud", "/") or ruta.startswith("/static")
        if not (ruidosa and respuesta.status_code < 400):
            nivel = _log.warning if respuesta.status_code >= 500 else _log.info
            nivel(
                "%s %s -> %d (%.0f ms)",
                request.method,
                ruta,
                respuesta.status_code,
                ms,
            )
        return respuesta

    # --- Manejadores de errores -----------------------------------------
    @app.exception_handler(DomainError)
    async def _domain_error(_: Request, exc: DomainError) -> JSONResponse:
        # Errores esperados de negocio (404, 409, 422...). No son fallos del
        # sistema; se registran en INFO para tener trazabilidad sin ruido.
        _log.info("Error de dominio %d: %s", exc.status_code, exc.mensaje)
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.mensaje})

    @app.exception_handler(RequestValidationError)
    async def _validacion(_: Request, exc: RequestValidationError) -> JSONResponse:
        _log.info("Datos de entrada inválidos: %s", exc.errors())
        return JSONResponse(status_code=422, content={"detail": exc.errors()})

    @app.exception_handler(Exception)
    async def _inesperado(request: Request, exc: Exception) -> JSONResponse:
        _log.exception("Error inesperado en %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=500,
            content={"detail": "Error interno del servidor. Revisá los logs."},
        )

    # --- Endpoints de servicio -----------------------------------------
    @app.get("/salud", tags=["servicio"], summary="Chequeo de salud")
    async def salud() -> dict:
        bd_ok = await verificar_conexion()
        return {"estado": "ok" if bd_ok else "degradado", "base_de_datos": bd_ok}

    # --- Routers de features -------------------------------------------
    app.include_router(terceros_router)
    app.include_router(facturas_router)
    app.include_router(contratos_router)
    app.include_router(movimientos_router)
    app.include_router(contabilidad_router)

    # --- Interfaz gráfica HTML (feature web-ui) ------------------------
    # Se monta al final: las rutas de la API ya están registradas y tienen
    # prioridad. Ver docs/features/web-ui/spec.md.
    app.mount("/static", StaticFiles(directory=_WEB), name="static")

    @app.get("/", include_in_schema=False)
    async def _home() -> FileResponse:
        return FileResponse(_WEB / "index.html")

    return app


app = create_app()
