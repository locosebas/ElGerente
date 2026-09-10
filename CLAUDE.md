# El Gerente — guía para sesiones de IA

Herramienta de contabilidad para **una sola empresa**: motor contable determinístico
(partida doble) + interfaz web, y a futuro un chatbot de WhatsApp. El dueño audita el
trabajo; explicá antes de implementar y avanzá en pasos chicos.

## Empezá por acá — orden de lectura barato en tokens

1. **[`docs/ESTADO.md`](docs/ESTADO.md)** — qué está hecho, qué falta, cómo correr y probar.
2. **[`docs/MAPA.md`](docs/MAPA.md)** — tabla "quiero cambiar X → archivo + símbolo + spec"
   + reglas de arquitectura que no se rompen + grafo de dependencias.
3. **[`docs/TAREAS.md`](docs/TAREAS.md)** — backlog priorizado; cada tarea sirve como un chat.
4. **[`docs/PARA-NUEVO-CHAT.md`](docs/PARA-NUEVO-CHAT.md)** — prompts de arranque, cómo
   partir el trabajo en varios chats/agentes sin pisarse, checklist de cierre.
5. Solo el `spec.md` de la feature que vas a tocar: `docs/features/<feature>/spec.md`.

Para la línea exacta de un símbolo: `grep -n "def <nombre>" <archivo>` — no busques a ciegas.
Índice de todo el código en un archivo: [`docs/_generado/indice-codigo.md`](docs/_generado/indice-codigo.md)
(generado; `python scripts/generar_mapa.py` lo regenera; hay un test que falla si quedó viejo).

**NO leas** salvo que la tarea lo pida: toda la carpeta `analysis/` (es historial de
brainstorming, no el estado actual), todos los specs a la vez, ni el plan en
`~/.claude/plans/` (su parte pendiente está en `docs/TAREAS.md`).

## Flujo de trabajo (lo pidió el dueño)

Por feature, **en este orden**: escribir/actualizar `docs/features/<feature>/spec.md` →
implementar → escribir los tests de la sección "Casos de prueba" del spec → marcar estado
en el spec y en `docs/features/README.md`.

`analysis/` es historial de decisiones (no se edita). `docs/` es la documentación viva.

## Reglas que no se rompen

- Lógica de negocio **solo** en los `service.py`; los `router.py` solo traducen HTTP.
- Nadie escribe en las tablas contables sin pasar por `app/contabilidad/asientos.py::crear_asiento`.
- Los servicios lanzan errores de dominio (`app/core/errors.py`), nunca `HTTPException`.
- Todo async; config solo desde `app/core/config.py`.
- Cada asiento registra su `tercero_id` (con qué actor externo se hizo).
- El chatbot de WhatsApp (Módulo 2) es **100 % determinístico** — sin IA en ningún punto.

## Comandos

```bash
cd backend
.venv/bin/python -m pytest -q               # ~90 tests, deben pasar (ver número exacto en ESTADO.md)
.venv/bin/ruff check .
.venv/bin/python scripts/reset_db.py        # recrea la BD + plan de cuentas
.venv/bin/python scripts/seed_demo.py       # datos de demostración
.venv/bin/uvicorn app.main:app --reload     # http://localhost:8000/
python ../scripts/generar_mapa.py           # regenerar el índice de código
```

Commits: rama de feature (no `main`), mensajes en español, terminar con
`Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>`.
Rama de trabajo actual: `feat/v1-modulo-1-arquitectura-features` (aún sin mergear a `main`).
