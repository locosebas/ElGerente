"""Reinicia la base de datos de desarrollo desde cero.

Borra el archivo SQLite, aplica todas las migraciones y vuelve a sembrar
el plan de cuentas. Solo para desarrollo (no tocar en producción).

    python scripts/reset_db.py
"""
from __future__ import annotations

import asyncio
import subprocess
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent


def main() -> None:
    db = BACKEND / "elgerente.db"
    if db.exists():
        db.unlink()
        print(f"Borrado {db.name}")

    print("alembic upgrade head ...")
    # `python -m alembic` en vez de `alembic` a secas: funciona aunque el bin
    # del entorno virtual no esté en el PATH.
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"], cwd=BACKEND, check=True
    )

    sys.path.insert(0, str(BACKEND))
    from app.seed import seed

    asyncio.run(seed())


if __name__ == "__main__":
    main()
