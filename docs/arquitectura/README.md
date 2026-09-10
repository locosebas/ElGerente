# Arquitectura

Decisiones técnicas transversales del proyecto.

- **[`vista-general.html`](vista-general.html)** — página HTML con la arquitectura de un
  vistazo: capas, flujo de una petición, grafo de dependencias, inventario de features,
  base de datos y decisiones. Abrila en el navegador (o publicada como Artifact en
  claude.ai — buscar "Arquitectura de El Gerente").
- [`vision-tecnica.md`](vision-tecnica.md) — las piezas, las capas y por qué async, en texto.
- [`base-de-datos.md`](base-de-datos.md) — SQLAlchemy async, SQLite → PostgreSQL, migraciones Alembic.
- [`testing.md`](testing.md) — unit vs. integración, fixtures, cómo se corre.
- [`resiliencia-y-logs.md`](resiliencia-y-logs.md) — errores, transacciones, `/salud`, logs.
- [`despliegue.md`](despliegue.md) — Docker y subida a la nube.

El grafo de dependencias también está en texto en [`../MAPA.md`](../MAPA.md).
