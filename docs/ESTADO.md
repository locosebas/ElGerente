# Estado del proyecto — El Gerente

_Última actualización: 2026-09-09_

Resumen: el **Módulo 1 (motor contable)** y su **interfaz gráfica HTML** están completos —
arquitectura por features, base de datos asíncrona, 59 pruebas en verde. La documentación
por feature está al día. Falta todo el Módulo 2 (WhatsApp).

---

## Avance por etapas del plan

| Etapa | Qué es | Estado |
|---|---|---|
| 0 | Esqueleto y herramientas (pyproject, config, engine async, Alembic, fixtures de test) | ✅ hecho |
| 1 | Documentación del Módulo 1 (7 specs + arquitectura + aprendizaje) | ✅ hecho |
| 2 | Migrar Módulo 1 a async + arquitectura por features + tests | ✅ hecho — 56 tests en verde |
| 2b | Interfaz gráfica HTML del Módulo 1 | ✅ hecho — 3 tests más (59 en total) |
| 3 | Documentación del Módulo 2 (specs de las features de WhatsApp) | ⬜ pendiente — **lo próximo** |
| 4 | Construir el Módulo 2 (webhook, conversaciones, asistente, flujos) | ⬜ pendiente |
| 5 | Cierre (script de simulación, catálogo final, READMEs) | ⬜ pendiente |

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
  alembic/                  migraciones (0001_esquema_inicial: las 6 tablas del Módulo 1)
  app/
    core/                   config (.env), engine async, errores de dominio
    contabilidad/           NÚCLEO: cuenta/asiento/linea_asiento, crear_asiento (partida doble),
                            balance (consulta SQL), plan de cuentas, router de solo lectura
    features/
      terceros/             clientes y proveedores
      facturas/             registrar factura -> asiento automático
      pagos/                pagar/cobrar factura -> asiento automático + estado
      contratos/            registro informativo (no toca contabilidad)
      movimientos/          asiento manual: oficial (con soporte) / interno (para-contabilidad)
    web/                  interfaz gráfica: index.html + app.js + styles.css (JS plano)
    main.py                 create_app(): routers + errores a HTTP + monta la interfaz en /
    models.py               agregador de modelos (para Alembic y tests)
    seed.py                 siembra el plan de cuentas (NO crea tablas)
  scripts/reset_db.py       borra la BD, migra y siembra (desarrollo)
  tests/
    unit/                   34 tests — reglas de negocio, servicios llamados directo
    integration/            25 tests — app real vía httpx.AsyncClient + SQLite temporal

docs/
  README.md                índice de la documentación
  ESTADO.md                este archivo
  arquitectura/            vision-tecnica, base-de-datos, testing
  aprendizaje/             partida-doble, que-es-una-api, async-await, deterministico-vs-ia
  features/
    README.md              índice de las 17 features con su estado
    pruebas.md             catálogo de las 59 pruebas
    <feature>/spec.md      una por feature (las 7 del Módulo 1 + web-ui)
```

### Endpoints disponibles (Módulo 1)

`POST/GET /terceros` · `POST/GET /facturas` · `GET /facturas/{id}` ·
`POST /facturas/{id}/pagar` · `POST/GET /contratos` · `POST /movimientos` ·
`GET /cuentas` · `GET /asientos` (filtro `?libro=`) · `GET /balance` (`?incluir_interna=`)

- `http://localhost:8000/` → interfaz gráfica HTML
- `http://localhost:8000/docs` → documentación interactiva de la API

---

## Pruebas

- **59 pruebas, todas pasan.** `pytest` desde `backend/`.
- 34 unitarias + 25 de integración.
- Incluye un test que verifica que el esquema de los modelos y el de las migraciones no se
  separen (`test_no_hay_migracion_pendiente`).
- Catálogo completo con una línea por test: [`features/pruebas.md`](features/pruebas.md).

---

## Cómo verificar el estado por tu cuenta

```bash
cd backend
uv venv --python 3.12
uv pip install -e ".[dev]"
cp .env.example .env

.venv/bin/python -m pytest -q            # -> 59 passed
.venv/bin/ruff check .                   # -> All checks passed

.venv/bin/alembic upgrade head
.venv/bin/python -m app.seed
.venv/bin/uvicorn app.main:app --reload  # http://localhost:8000/  (interfaz)  y  /docs (API)
```

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

**Etapa 3 — documentar el Módulo 2 (WhatsApp).** Escribir el `spec.md` de cada feature de
WhatsApp (proveedor, webhook, conversaciones, asistente, y los flujos de factura, pago,
contrato, movimiento y consulta de balance): payloads de ejemplo, pasos de cada flujo,
textos del menú y de la ayuda, tabla `conversacion`. Después, la Etapa 4 los construye.
Recordatorio: **el chatbot es 100 % determinístico**.
