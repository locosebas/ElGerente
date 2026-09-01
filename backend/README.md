# Backend — Módulo 1 (Motor Contable Básico)

Ver diseño en `../analysis/01-features/modulo-1-motor-contable.md`,
`../analysis/04-data-model/modulo-1-modelo-datos.md` y, sobre todo,
`../analysis/02-architecture/modulo-1-api-design.md` (reglas exactas
de generación automática de asientos — léelo antes de tocar `app/services.py`).

## Qué hay hasta ahora

- `app/db.py` — conexión a la base de datos (SQLite por ahora)
- `app/models.py` — tablas: `cuenta`, `tercero`, `asiento`, `linea_asiento`, `factura`, `contrato`
- `app/schemas.py` — forma de los datos que entran/salen por la API (Pydantic)
- `app/services.py` — toda la lógica de negocio (generación de asientos, validaciones). Los routers nunca deciden contabilidad por su cuenta.
- `app/main.py` — endpoints FastAPI: terceros, facturas (con pago), contratos, cuentas, asientos, balance
- `app/seed.py` — crea las tablas y siembra el plan de cuentas inicial
- `smoke_test.py` — prueba manual del modelo de datos solo (regla débito=crédito)
- `api_smoke_test.py` — prueba de extremo a extremo de la API completa (crear tercero, factura, pagar, balance, casos de error)

## Cómo correrlo

```bash
cd backend
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt

./.venv/bin/python -m app.seed          # crea elgerente.db y siembra el plan de cuentas
./.venv/bin/python smoke_test.py        # verifica el modelo de datos
./.venv/bin/python api_smoke_test.py    # verifica la API completa (borra y recrea elgerente.db)

# Para levantar el servidor y probar a mano (http://localhost:8000/docs trae la UI interactiva):
./.venv/bin/uvicorn app.main:app --reload
```

`elgerente.db` se genera localmente y no se sube al repo (ver `.gitignore`).

## Endpoints

Ver la tabla completa en `analysis/02-architecture/modulo-1-api-design.md#3-endpoints`.
Resumen: `POST/GET /terceros`, `POST/GET /facturas`, `GET /facturas/{id}`,
`POST /facturas/{id}/pagar`, `POST/GET /contratos`, `GET /cuentas`,
`GET /asientos`, `GET /balance`.
