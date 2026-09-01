# Backend — Módulo 1 (Motor Contable Básico)

Ver diseño en `../analysis/01-features/modulo-1-motor-contable.md` y
`../analysis/04-data-model/modulo-1-modelo-datos.md`.

## Qué hay hasta ahora

- `app/db.py` — conexión a la base de datos (SQLite por ahora)
- `app/models.py` — tablas: `cuenta`, `tercero`, `asiento`, `linea_asiento`, `factura`, `contrato`
- `app/seed.py` — crea las tablas y siembra el plan de cuentas inicial
- `smoke_test.py` — prueba manual de que la regla de partida doble (débitos = créditos) funciona

Todavía no hay API (eso es el siguiente paso: exponer endpoints con FastAPI para registrar y consultar).

## Cómo correrlo

```bash
cd backend
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
./.venv/bin/python -m app.seed        # crea elgerente.db y siembra el plan de cuentas
./.venv/bin/python smoke_test.py      # verifica que la partida doble se valida bien
```

`elgerente.db` se genera localmente y no se sube al repo (ver `.gitignore`).
