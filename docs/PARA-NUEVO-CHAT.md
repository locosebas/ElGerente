# Cómo empezar un chat nuevo sin recargar contexto

El objetivo es que una sesión nueva (o un agente) se vuelva productiva leyendo **poco**, y
que se pueda **partir el trabajo en varios chats/agentes** sin pisarse.

---

## 1. Arranque barato (lo mínimo a leer)

`CLAUDE.md` se carga solo. A partir de ahí, para casi cualquier tarea alcanza con:

1. **[`ESTADO.md`](ESTADO.md)** — qué está hecho, qué falta, cómo correr y probar.
2. **[`MAPA.md`](MAPA.md)** — tabla "quiero cambiar X → archivo + símbolo + spec".
3. El **`spec.md` de la feature** que vas a tocar (solo ese).
4. Para ubicar un símbolo: `grep -n "def <nombre>" backend/app/.../<archivo>.py`
   (o mirar [`_generado/indice-codigo.md`](_generado/indice-codigo.md), que es todo el
   código en un archivo).

**NO leas** (salvo que la tarea lo pida explícitamente):
- toda la carpeta `analysis/` — es historial de brainstorming, no el estado actual;
- todos los `spec.md` a la vez;
- el plan completo en `~/.claude/plans/` — su parte pendiente ya está resumida en
  [`TAREAS.md`](TAREAS.md);
- el código de features que no vas a tocar.

---

## 2. Prompts de arranque según el tipo de tarea

Copiá el que aplique al abrir el chat nuevo.

**Bug o cambio chico en una feature del Módulo 1**
> Trabajamos en El Gerente. Leé `docs/ESTADO.md` y `docs/MAPA.md`. La tarea: <describir>.
> Es en la feature `<nombre>` — leé solo `docs/features/<nombre>/spec.md`. Seguí el flujo
> spec → código → tests. Corré `pytest` desde `backend/` al terminar.

**Una tarea del backlog**
> Trabajamos en El Gerente. Leé `docs/ESTADO.md`, `docs/MAPA.md` y `docs/TAREAS.md`.
> Vamos con la tarea `<A1 / B1 / C3 / ...>`. Empezá por lo que esa entrada indique.

**Documentar el Módulo 2 (specs de WhatsApp)**
> Trabajamos en El Gerente. Leé `docs/ESTADO.md` y `docs/aprendizaje/deterministico-vs-ia.md`.
> Vamos a escribir el `spec.md` de `<feature de whatsapp>` en `docs/features/`, usando la
> plantilla `docs/features/_PLANTILLA-spec.md`. El chatbot es 100 % determinístico.

**Solo revisar / entender algo (sin cambiar código)**
> Trabajamos en El Gerente. Leé `docs/MAPA.md`. Pregunta: <...>. Respondé sin abrir más
> archivos de los necesarios.

---

## 3. Trabajar en paralelo (varios chats / agentes)

### Regla de oro
Cada tarea, **su propia rama** desde `feat/v1-modulo-1-arquitectura-features` (o desde
`main` cuando esa rama esté mergeada). Commits chicos. Merge frecuente.

### Qué se puede tocar en paralelo sin conflicto
- **Cada carpeta de feature es independiente**: `app/features/terceros/`,
  `.../facturas/`, `.../whatsapp/flows/factura.py`, etc. Dos agentes en dos features
  distintas casi no chocan.
- Los `docs/features/<feature>/spec.md` son independientes entre sí.

### Archivos "calientes" — coordinar / hacer de a uno
Si dos tareas los tocan a la vez, hay merge manual:

| Archivo | Por qué |
|---|---|
| `backend/app/main.py` | todas las features registran su router acá |
| `backend/app/models.py` | agregador — cada modelo nuevo se importa acá |
| `backend/app/contabilidad/**` | núcleo compartido: lo usa todo |
| `backend/alembic/versions/**` | dos migraciones nuevas en paralelo = cadena rota (renumerar) |
| `backend/tests/conftest.py` | fixtures compartidas |
| `backend/scripts/seed_demo.py` | datos de demostración |
| `docs/ESTADO.md`, `docs/features/README.md`, `docs/features/pruebas.md` | índices |
| `docs/_generado/indice-codigo.md` | generado — regenerar y commitear al final, no editar |
| `CLAUDE.md`, `docs/MAPA.md`, `docs/TAREAS.md` | navegación |

**Estrategia**: quien hace la tarea toca su feature libremente y deja los archivos calientes
para un commit final chico y separado ("wire-up"), que es fácil de mergear o rehacer.

### División sugerida del Módulo 2 en paralelo
1. Agente/chat A: infraestructura — `whatsapp-proveedor`, `whatsapp-webhook`,
   `whatsapp-conversaciones`, `whatsapp-asistente`.
2. Cuando A esté mergeado, en paralelo: un chat por flujo (`flujo-factura`, `flujo-pago`,
   `flujo-contrato`, `flujo-movimiento`, `consulta-balance`) — todos dependen de la
   infraestructura pero no entre sí.

---

## 4. Checklist para cerrar cualquier tarea

- [ ] `spec.md` de la feature actualizado (reglas + casos de prueba + estado).
- [ ] `cd backend && .venv/bin/python -m pytest -q` → todo verde.
- [ ] `.venv/bin/ruff check .` → limpio.
- [ ] Si tocaste `app/**/*.py`: `python scripts/generar_mapa.py` y commitear el índice.
- [ ] `docs/ESTADO.md` y `docs/features/README.md` reflejan el cambio.
- [ ] `docs/features/pruebas.md` lista los tests nuevos.
- [ ] Commits en la rama de la tarea, mensajes en español, cerrando con
      `Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>`.
- [ ] `git push` si el dueño lo pidió.

---

## 5. Cómo levantar el proyecto (recordatorio corto)

```bash
cd backend
uv venv --python 3.12 && uv pip install -e ".[dev]" && cp .env.example .env   # solo la 1a vez
.venv/bin/python scripts/reset_db.py      # tablas + plan de cuentas
.venv/bin/python scripts/seed_demo.py     # datos de demostración (opcional)
.venv/bin/uvicorn app.main:app --reload   # http://localhost:8000/
```

Detalle completo en `ESTADO.md` y `backend/README.md`.
