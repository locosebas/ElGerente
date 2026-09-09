# Imagen del backend de El Gerente.
#
# Diseño pensado para desplegar fácil en cualquier nube:
# - configuración 100% por variables de entorno (12-factor);
# - la app es sin estado: los datos viven en la base de datos externa;
# - corre como usuario sin privilegios;
# - los logs van a stdout;
# - el puerto se toma de $PORT (por defecto 8000).
#
# Contexto de build: la carpeta backend/  (ver docker-compose.yml).

# --- Etapa 1: dependencias (capa cacheable) --------------------------------
FROM python:3.12-slim AS deps

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Solo el manifiesto + un paquete vacío: si no cambian las dependencias,
# esta capa se reutiliza aunque cambie el código.
COPY pyproject.toml README.md ./
RUN mkdir app && touch app/__init__.py \
    && pip install --no-cache-dir .

# --- Etapa 2: imagen final -----------------------------------------------
FROM python:3.12-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    ENTORNO=prod

WORKDIR /app

# Paquetes Python ya instalados en la etapa anterior.
COPY --from=deps /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin

# Código de la aplicación (lo que .dockerignore no excluye).
COPY . .

RUN chmod +x docker-entrypoint.sh \
    && useradd --system --no-create-home elgerente \
    && chown -R elgerente /app
USER elgerente

EXPOSE 8000

# El entrypoint aplica migraciones, siembra el plan de cuentas y arranca uvicorn.
ENTRYPOINT ["./docker-entrypoint.sh"]
