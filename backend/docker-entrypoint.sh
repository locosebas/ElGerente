#!/bin/sh
# Arranque del contenedor: prepara la base de datos y levanta el servidor.
#
# Nota para la nube: aplicar migraciones aquí funciona bien con UNA instancia.
# Con varias instancias en paralelo conviene mover `alembic upgrade head` a un
# job de despliegue aparte y dejar aquí solo el `uvicorn`.
set -e

echo "[entrypoint] Esperando a la base de datos y aplicando migraciones..."
# Reintenta unos segundos: en compose/nube la BD puede tardar en aceptar conexiones.
n=0
until alembic upgrade head; do
  n=$((n + 1))
  if [ "$n" -ge 10 ]; then
    echo "[entrypoint] La base de datos no respondió tras 10 intentos. Abortando."
    exit 1
  fi
  echo "[entrypoint] Reintentando en 3s... ($n/10)"
  sleep 3
done

echo "[entrypoint] Sembrando el plan de cuentas (idempotente)..."
python -m app.seed

echo "[entrypoint] Arrancando el servidor en el puerto ${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" --proxy-headers --forwarded-allow-ips '*'
