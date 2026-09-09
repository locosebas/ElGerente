# Estado del proyecto — El Gerente

_Última actualización: 2026-09-09_

Resumen: el **Módulo 1 (motor contable)**, su **interfaz gráfica HTML** y el
**endurecimiento** (resiliencia a fallos, logs, endpoint de salud, imagen Docker) están
listos — arquitectura por features, base de datos asíncrona, **65 pruebas en verde**.
Listo para montar en local y probar con clientes de verdad. Falta el Módulo 2 (WhatsApp).

---

## Avance por etapas del plan

| Etapa | Qué es | Estado |
|---|---|---|
| 0 | Esqueleto y herramientas (pyproject, config, engine async, Alembic, fixtures de test) | ✅ hecho |
| 1 | Documentación del Módulo 1 (7 specs + arquitectura + aprendizaje) | ✅ hecho |
| 2 | Migrar Módulo 1 a async + arquitectura por features + tests | ✅ hecho — 56 tests en verde |
| 2b | Interfaz gráfica HTML del Módulo 1 | ✅ hecho — 59 tests |
| 2c | Endurecimiento: congruencia, resiliencia a fallos, logs, `/salud`, Docker | ✅ hecho — 65 tests |
| 3 | Documentación del Módulo 2 (specs de las features de WhatsApp) | ⬜ pendiente |
| 4 | Construir el Módulo 2 (webhook, conversaciones, asistente, flujos) | ⬜ pendiente |
| 5 | Cierre (script de simulación, catálogo final, READMEs) | ⬜ pendiente |

Ahora mismo el foco es **probar el Módulo 1 con clientes reales** antes de seguir con el
Módulo 2.

Plan completo aprobado: `/home/locosebas/.claude/plans/` ("El Gerente v1: Módulo 1 + Módulo 2").

---

## Avance por feature

Leyenda: ✅ hecho y verificado · 🟨 en progreso · ⬜ pendiente

### Módulo 1 — motor contable

| # | Feature | Estado | Código | Spec |
|---|---|---|---|---|
| 1 | `contabilidad-nucleo` | ✅ | `backend/app/contabilidad/` | [spec](features/contabilidad-nucleo/spec.md) |
| 2 | `balance` | ✅ | `backend/app/contabilidad/balance.py` | [spec](features/balance/spec.md) |
| 3 | `terceros` | ✅ | `backend/app/features/terceros/` | [spec](features/terceros/spec.md) |
| 4 | `facturas` | ✅ | `backend/app/features/facturas/` | [spec](features/facturas/spec.md) |
| 5 | `pagos` | ✅ | `backend/app/features/pagos/` | [spec](features/pagos/spec.md) |
| 6 | `contratos` | ✅ | `backend/app/features/contratos/` | [spec](features/contratos/spec.md) |
| 7 | `movimientos` | ✅ | `backend/app/features/movimientos/` | [spec](features/movimientos/spec.md) |

### Módulo 2 — WhatsApp (chatbot 100 % determinístico)

| # | Feature | Estado | Notas |
|---|---|---|---|
| 8 | `whatsapp-proveedor` | ⬜ | interfaz `ProveedorWhatsApp` + `Fake` + stub Meta |
| 9 | `whatsapp-webhook` | ⬜ | verificación + recepción de mensajes |
| 10 | `whatsapp-conversaciones` | ⬜ | motor de máquina de estados + persistencia |
| 11 | `whatsapp-asistente` | ⬜ | saludo, menú, `ayuda`, `cancelar`, detección de intención, fallback |
| 12 | `whatsapp-flujo-factura` | ⬜ | |
| 13 | `whatsapp-flujo-pago` | ⬜ | |
| 14 | `whatsapp-flujo-contrato` | ⬜ | |
| 15 | `whatsapp-flujo-movimiento` | ⬜ | incluye consignación |
| 16 | `whatsapp-consulta-balance` | ⬜ | |

### Transversal

| # | Feature | Estado | Notas |
|---|---|---|---|
| 17 | `web-ui` (interfaz gráfica HTML) | ✅ | 6 pantallas (balance, libro diario, terceros, facturas, contratos, movimiento manual); servida en `/` |

---

## Qué existe hoy en el código

```
backend/
  pyproject.toml            dependencias + config de pytest/ruff
  .env.example              variables de entorno documentadas
  Dockerfile                imagen del backend (multi-etapa, usuario sin privilegios)
  docker-entrypoint.sh      arranque: migraciones -> seed -> uvicorn
  .dockerignore
  alembic/                  migraciones (0001_esquema_inicial: las 6 tablas del Módulo 1)
  app/
    core/                   config (.env), engine async, logging, errores de dominio
    contabilidad/           NÚCLEO: cuenta/asiento/linea_asiento, crear_asiento (partida doble),
                            balance (consulta SQL), plan de cuentas, serializador, router
    features/
      terceros/             clientes y proveedores
      facturas/             registrar factura -> asiento automático
      pagos/                pagar/cobrar factura -> asiento automático + estado
      contratos/            registro informativo (no toca contabilidad)
      movimientos/          asiento manual: oficial (con soporte) / interno (para-contabilidad)
    web/                    interfaz gráfica: index.html + app.js + styles.css (JS plano)
    main.py                 create_app(): lifespan, logging por petición, manejo de errores,
                            /salud, routers y montaje de la interfaz en /
    models.py               agregador de modelos (para Alembic y tests)
    seed.py                 siembra el plan de cuentas (NO crea tablas)
  scripts/reset_db.py       borra la BD, migra y siembra (desarrollo)
  tests/
    unit/                   34 tests — reglas de negocio, servicios llamados directo
    integration/            31 tests — app real vía httpx.AsyncClient + SQLite temporal

docker-compose.yml          app + PostgreSQL para probar en local
.env.docker.example

docs/
  README.md                índice de la documentación
  ESTADO.md                este archivo
  arquitectura/            vision-tecnica, base-de-datos, testing, resiliencia-y-logs, despliegue
  aprendizaje/             partida-doble, que-es-una-api, async-await, deterministico-vs-ia
  features/
    README.md              índice de las 17 features con su estado
    pruebas.md             catálogo de las 65 pruebas
    <feature>/spec.md      una por feature (las 7 del Módulo 1 + web-ui)
```

### Endpoints disponibles (Módulo 1)

`POST/GET /terceros` · `POST/GET /facturas` · `GET /facturas/{id}` ·
`POST /facturas/{id}/pagar` · `POST/GET /contratos` · `POST /movimientos` ·
`GET /cuentas` · `GET /asientos` (filtro `?libro=`) · `GET /balance` (`?incluir_interna=`)

- `http://localhost:8000/` → interfaz gráfica HTML
- `http://localhost:8000/docs` → documentación interactiva de la API
- `http://localhost:8000/salud` → chequeo de salud (para Docker / la nube)

---

## Pruebas

- **65 pruebas, todas pasan.** `pytest` desde `backend/`.
- 34 unitarias + 31 de integración.
- Cubren: reglas contables, generación de asientos, libros oficial/interno, la API de punta
  a punta, la interfaz gráfica, que modelos y migraciones no se separen, y la resiliencia
  (500 genérico ante fallos, `/salud`, errores de dominio y validación).
- Catálogo completo con una línea por test: [`features/pruebas.md`](features/pruebas.md).

---

## Cómo verlo / montarlo en local

### Opción rápida (SQLite, sin Docker)

```bash
cd backend
uv venv --python 3.12
uv pip install -e ".[dev]"
cp .env.example .env

.venv/bin/python -m pytest -q            # -> 65 passed
.venv/bin/ruff check .                   # -> All checks passed

.venv/bin/alembic upgrade head
.venv/bin/python -m app.seed
.venv/bin/uvicorn app.main:app --reload  # http://localhost:8000/  (interfaz)  y  /docs (API)
```

### Con Docker (app + PostgreSQL, igual que la nube)

```bash
cp .env.docker.example .env.docker
docker compose --env-file .env.docker up --build
# http://localhost:8000/
```

Detalle en [`arquitectura/despliegue.md`](arquitectura/despliegue.md).

---

## Decisiones tomadas hasta ahora

| Tema | Decisión |
|---|---|
| Alcance de v1 | Módulo 1 (motor contable) + Módulo 2 (WhatsApp, registro guiado) |
| Arquitectura | Por features (carpeta autocontenida por parte del programa) |
| Asincronismo | Async en todo (FastAPI, SQLAlchemy, httpx, pytest) |
| Base de datos | SQLite hoy → PostgreSQL cambiando una variable; esquema por migraciones Alembic |
| Chatbot de WhatsApp | 100 % determinístico — sin IA en ningún punto |
| Asistente de WhatsApp | Feature propia, determinística, alcance: solo uso de la plataforma |
| Proveedor de WhatsApp (Meta vs Twilio) | Sin decidir — se construye contra una interfaz con adaptador `Fake` |
| Documentación | `docs/features/<feature>/`; `analysis/` queda como historial |
| Forma de trabajo | Por feature: spec → código → tests, en ese orden |

---

## Lo próximo

1. **Probar el Módulo 1 con clientes de verdad.** Montarlo en local (interfaz en `/`),
   registrar datos reales unos días, y anotar lo que falte o incomode.
2. Con eso, cerrar los huecos que aparezcan (validaciones, campos, textos).
3. Recién entonces, **Etapa 3**: documentar el Módulo 2 (WhatsApp) y construirlo.
   Recordatorio: el chatbot es **100 % determinístico**.

### Pendiente conocido antes de exponerlo fuera de una red de confianza

- **Autenticación / login**: hoy no hay (una sola persona). Ver
  [`arquitectura/despliegue.md`](arquitectura/despliegue.md).
- La imagen Docker está escrita y revisada pero **no se pudo construir en este entorno**
  (sin permisos de Docker); conviene un `docker compose up --build` de verificación.
