# Despliegue (Docker y nube)

## Idea

- **En local para probar**: `docker compose up` levanta la app + PostgreSQL.
- **En la nube**: se sube **la imagen del backend** (`backend/Dockerfile`) a cualquier
  servicio de contenedores (Cloud Run, Render, Fly.io, ECS, Railway...) y se le da una base
  de datos PostgreSQL gestionada. No hace falta cambiar código.

La imagen sigue los principios *12-factor*:
- **toda la configuración es por variables de entorno** (no hay nada "quemado" en el código);
- **la app no guarda estado**: los datos viven en la base de datos externa, así se puede
  correr una o varias copias;
- **los logs van a stdout**;
- **corre como usuario sin privilegios**;
- **el puerto se toma de `$PORT`** (por defecto 8000).

## Probar en local con Docker

```bash
cp .env.docker.example .env.docker      # ajustar POSTGRES_PASSWORD si se quiere
docker compose --env-file .env.docker up --build
```

- Interfaz gráfica: <http://localhost:8000/>
- API: <http://localhost:8000/docs>
- Salud: <http://localhost:8000/salud>

`docker compose down` para parar; `docker compose down -v` para borrar también los datos.

> Para una mirada rápida **sin Docker ni PostgreSQL**, no hace falta nada de esto: ver
> `backend/README.md` (uvicorn directo sobre SQLite).

## Qué hace el contenedor al arrancar

`backend/docker-entrypoint.sh`:
1. `alembic upgrade head` — aplica las migraciones (reintenta hasta 10 veces si la BD aún
   no acepta conexiones);
2. `python -m app.seed` — siembra el plan de cuentas (idempotente);
3. `uvicorn app.main:app` — arranca el servidor.

## Variables de entorno

| Variable | Para qué | Ejemplo |
|---|---|---|
| `DATABASE_URL` | conexión a la base de datos | `postgresql+asyncpg://usuario:clave@host:5432/elgerente` |
| `ENTORNO` | `dev` o `prod` | `prod` |
| `LOG_LEVEL` | detalle de los logs | `INFO` |
| `PORT` | puerto del servidor | `8000` |
| `WHATSAPP_*` | credenciales del Módulo 2 (todavía no se usa) | — |

## Subir a la nube (esquema general)

1. Construir y publicar la imagen:
   ```bash
   docker build -t <tu-registro>/elgerente-backend:v1 ./backend
   docker push <tu-registro>/elgerente-backend:v1
   ```
2. Crear una base de datos **PostgreSQL gestionada** en el proveedor.
3. Desplegar la imagen como servicio de contenedor, con:
   - `DATABASE_URL` apuntando a esa base de datos,
   - `ENTORNO=prod`,
   - el healthcheck contra `GET /salud`.

### Nota sobre migraciones con varias instancias

El entrypoint corre `alembic upgrade head` al arrancar. Con **una** instancia está bien.
Si se corren **varias instancias en paralelo**, conviene mover ese paso a un *job* de
despliegue aparte (que corra una sola vez) y dejar en el entrypoint solo el `uvicorn`.

## Qué falta para "listo para clientes de verdad"

- **Copias de seguridad** de la base de datos (lo da el PostgreSQL gestionado del proveedor).
- **HTTPS**: lo pone el balanceador/proxy del proveedor de nube; la app ya envía
  `--proxy-headers`.
- **Autenticación**: hoy no hay login (una sola persona). Antes de exponerlo fuera de una
  red de confianza hay que agregarlo.
