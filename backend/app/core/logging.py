"""Configuración de logging.

Objetivo: que los logs se entiendan sin conocer el código.

- Un solo formato para toda la app, con timestamp, nivel, logger y mensaje.
- Todo va a **stdout** (así lo recoge Docker / la nube sin configurar nada).
- Nivel configurable por entorno (`LOG_LEVEL` en el .env).
- Se nombra cada logger con `logging.getLogger("elgerente.<area>")` para
  poder filtrar por área (`elgerente.contabilidad`, `elgerente.http`...).

No se usa JSON estructurado todavía: para una sola empresa, texto legible
por humanos vale más. Si más adelante hace falta, se cambia solo aquí.
"""
from __future__ import annotations

import logging
import sys

_FORMATO = "%(asctime)s  %(levelname)-7s  %(name)s  %(message)s"
_FECHA = "%Y-%m-%d %H:%M:%S"

_configurado = False


def configurar_logging(nivel: str = "INFO") -> None:
    """Configura el logging raíz una sola vez. Idempotente."""
    global _configurado
    if _configurado:
        return

    raiz = logging.getLogger()

    # Añade nuestro handler solo si no hay ya uno nuestro (marcado con un
    # atributo). No se borran otros handlers: así no se pisa el que pytest
    # instala para capturar logs en los tests.
    if not any(getattr(h, "_elgerente", False) for h in raiz.handlers):
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(_FORMATO, datefmt=_FECHA))
        handler._elgerente = True  # type: ignore[attr-defined]
        raiz.addHandler(handler)

    raiz.setLevel(nivel.upper())

    # El logger de acceso de uvicorn duplica lo que ya registra nuestro
    # middleware; lo bajamos a WARNING para no tener cada request dos veces.
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    # El motor SQL es muy ruidoso en DEBUG; se deja en WARNING salvo que
    # explícitamente se quiera ver el SQL.
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    _configurado = True


def log(area: str) -> logging.Logger:
    """Devuelve el logger `elgerente.<area>`."""
    return logging.getLogger(f"elgerente.{area}")
