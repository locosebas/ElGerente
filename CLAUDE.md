# El Gerente — guía para sesiones de IA

Herramienta de contabilidad para **una sola empresa**: motor contable determinístico
(partida doble) + interfaz web, y a futuro un chatbot de WhatsApp. El dueño audita el
trabajo; explicá antes de implementar y avanzá en pasos chicos.

## Empezá por acá (para gastar pocos tokens)

1. **[`docs/MAPA.md`](docs/MAPA.md)** — te dice qué archivo y qué símbolo tocar para cada
   tipo de cambio, más las reglas de arquitectura que no hay que romper.
2. **[`docs/_generado/indice-codigo.md`](docs/_generado/indice-codigo.md)** — índice de
   todos los símbolos del código en un solo archivo (generado; regenerar con
   `python scripts/generar_mapa.py`).
3. **[`docs/ESTADO.md`](docs/ESTADO.md)** — qué está hecho y qué falta.
4. Para una feature concreta: `docs/features/<feature>/spec.md`.

Para la línea exacta de un símbolo: `grep -n "def <nombre>" <archivo>` — no busques a ciegas.

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
- El chatbot de WhatsApp (Módulo 2) es **100 % determinístico** — sin IA en ningún punto.

## Comandos

```bash
cd backend
.venv/bin/python -m pytest -q          # 65 tests, deben pasar
.venv/bin/ruff check .
.venv/bin/uvicorn app.main:app --reload   # http://localhost:8000/
python ../scripts/generar_mapa.py     # regenerar el índice de código
```

Commits: rama de feature (no `main`), mensajes en español, terminar con
`Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>`.
