"""Ensamblado de la aplicación FastAPI.

`create_app()` monta todos los routers de features y registra el manejador
que traduce los errores de dominio a respuestas HTTP. Ver
docs/arquitectura/vision-tecnica.md.
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# Registra todas las tablas en Base.metadata.
import app.models  # noqa: F401
from app.contabilidad.router import router as contabilidad_router
from app.core.errors import DomainError
from app.features.contratos.router import router as contratos_router
from app.features.facturas.router import router as facturas_router
from app.features.movimientos.router import router as movimientos_router
from app.features.terceros.router import router as terceros_router

_WEB = Path(__file__).parent / "web"


def create_app() -> FastAPI:
    app = FastAPI(title="El Gerente — Módulo 1: Motor Contable")

    @app.exception_handler(DomainError)
    async def _domain_error_handler(_: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.mensaje})

    app.include_router(terceros_router)
    app.include_router(facturas_router)
    app.include_router(contratos_router)
    app.include_router(movimientos_router)
    app.include_router(contabilidad_router)

    # Interfaz gráfica HTML (feature web-ui). Se monta al final: las rutas de la
    # API ya están registradas y tienen prioridad. Ver docs/features/web-ui/spec.md.
    app.mount("/static", StaticFiles(directory=_WEB), name="static")

    @app.get("/", include_in_schema=False)
    async def _home() -> FileResponse:
        return FileResponse(_WEB / "index.html")

    return app


app = create_app()
