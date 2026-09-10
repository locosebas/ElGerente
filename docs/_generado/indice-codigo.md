# Índice de código (generado)

> **Generado por `scripts/generar_mapa.py`. No editar a mano.**
> Regenerar: `python scripts/generar_mapa.py`.

Para la línea exacta de un símbolo: `grep -n "def <nombre>" <archivo>`.

## `backend/app/contabilidad/__init__.py`
_Núcleo contable: plan de cuentas, asientos de partida doble y balance._

## `backend/app/contabilidad/asientos.py`
_`crear_asiento` — el único punto de escritura contable._

  - `class DocumentoSoporteRequerido` — Un asiento de libro oficial siempre exige documento_soporte.
  - `class AsientoDesbalanceado` — La suma de débitos no iguala la de créditos.
  - `class CuentaInexistente` — Se pidió una cuenta que no está en el plan de cuentas.
  - `async def cuenta_por_codigo(session, codigo)` — 
  - `async def cuenta_requerida(session, codigo)` — Como `cuenta_por_codigo` pero exige que exista (para las reglas
  - `async def crear_asiento(session)` — Crea y valida un asiento. Hace `flush` (deja el id disponible),

  depende de: `app.contabilidad.models`, `app.core.errors`, `app.core.logging`

## `backend/app/contabilidad/balance.py`
_Cálculo del balance: saldo de cada cuenta, con filtro de libro y de periodo._

  - `class FiltroLibro` — 
  - `def condiciones_asiento(libro, desde, hasta, tercero_id)` — Filtros a aplicar sobre `asiento` (libro + rango de fechas + tercero).
  - `async def calcular_balance(session)` — Devuelve TODAS las cuentas del plan (incluso con saldo 0), ordenadas

  depende de: `app.contabilidad.models`, `app.core.errors`

## `backend/app/contabilidad/codigos.py`
_Códigos de cuenta usados por las reglas automáticas de asientos._

## `backend/app/contabilidad/detalle_cuenta.py`
_Extracto de una cuenta: sus movimientos con saldo acumulado._

  - `async def movimientos_de_cuenta(session, codigo)` — 

  depende de: `app.contabilidad.balance`, `app.contabilidad.models`, `app.core.errors`, `app.features.terceros.models`

## `backend/app/contabilidad/models.py`
_Modelos del núcleo contable — partida doble._

  - `class Naturaleza` — 
  - `class TipoCuenta` — 
  - `class OrigenAsiento` — 
  - `class LibroContable` — 
  - `class Cuenta` — 
  - `class Asiento` — 
  - `class LineaAsiento` — 

  depende de: `app.core.db`, `app.features.terceros.models`

## `backend/app/contabilidad/plan_cuentas.py`
_Plan de cuentas inicial y su siembra idempotente._

  - `async def sembrar_plan_de_cuentas(session)` — Inserta el plan de cuentas si aún no hay cuentas. Idempotente:

  depende de: `app.contabilidad.models`

## `backend/app/contabilidad/router.py`
_Endpoints de solo lectura del núcleo contable._

  - `async def listar_cuentas(db)` — 
  - `async def listar_asientos(libro, desde, hasta, tercero_id, db)` — 
  - `async def obtener_balance(libro, desde, hasta, tercero_id, db)` — 
  - `async def detalle_de_cuenta(codigo, libro, desde, hasta, tercero_id, db)` — 

  depende de: `app.contabilidad.balance`, `app.contabilidad.detalle_cuenta`, `app.contabilidad.models`, `app.contabilidad.schemas`, `app.contabilidad.serializers`, `app.core.db`

## `backend/app/contabilidad/schemas.py`
_Esquemas de entrada/salida del núcleo contable (Pydantic)._

  - `class CuentaOut` — 
  - `class LineaAsientoOut` — 
  - `class AsientoOut` — 
  - `class SaldoCuenta` — 
  - `class MovimientoCuentaOut` — 
  - `class DetalleCuentaOut` — 

  depende de: `app.contabilidad.models`

## `backend/app/contabilidad/serializers.py`
_Serialización de asientos a la forma que espera `AsientoOut`._

  - `def serializar_asiento(asiento)` — AsientoOut necesita cuenta_codigo/cuenta_nombre por línea, que viven

  depende de: `app.contabilidad.models`

## `backend/app/core/config.py`
_Configuración leída del entorno (archivo .env o variables reales)._

  - `class Settings` — 
  - `def get_settings()` — Se cachea: la configuración se lee una sola vez por proceso.

## `backend/app/core/db.py`
_Conexión a la base de datos — SQLAlchemy 2.0 en modo asíncrono._

  - `class Base` — Todos los modelos heredan de aquí; `Base.metadata` conoce todas las tablas.
  - `async def get_db()` — Entrega una sesión por petición.
  - `async def verificar_conexion()` — True si la base de datos responde a un `SELECT 1`.

  depende de: `app.core.config`, `app.core.logging`

## `backend/app/core/errors.py`
_Errores de dominio y su traducción a respuestas HTTP._

  - `class DomainError` — Base de todos los errores de negocio. `status_code` es el HTTP sugerido.
  - `class NoEncontrado` — 
  - `class Conflicto` — 
  - `class DatosInvalidos` — 
  - `def http_para(exc)` — 

## `backend/app/core/logging.py`
_Configuración de logging._

  - `def configurar_logging(nivel)` — Configura el logging raíz una sola vez. Idempotente.
  - `def log(area)` — Devuelve el logger `elgerente.<area>`.

## `backend/app/documentos/__init__.py`
_Enlaces a documentos de respaldo (RUT, PDF de factura/contrato)._

## `backend/app/documentos/enlace.py`
_Validación de un enlace a documento._

  - `def validar_enlace(valor)` — Normaliza y valida un enlace opcional.

  depende de: `app.core.errors`

## `backend/app/features/contratos/models.py`
_Modelo de `contrato` — registro informativo. Ver docs/features/contratos/spec.md._

  - `class EstadoContrato` — 
  - `class Contrato` — 

  depende de: `app.core.db`

## `backend/app/features/contratos/router.py`

  - `async def crear_contrato(data, db)` — 
  - `async def listar_contratos(db)` — 
  - `async def actualizar_enlace_documento(contrato_id, data, db)` — 

  depende de: `app.core.db`, `app.features.contratos`, `app.features.contratos.models`, `app.features.contratos.schemas`

## `backend/app/features/contratos/schemas.py`

  - `class ContratoCreate` — 
  - `class ContratoEnlace` — Cuerpo del PATCH: solo el enlace al PDF (puede ser null para quitarlo).
  - `class ContratoOut` — 

  depende de: `app.features.contratos.models`

## `backend/app/features/contratos/service.py`
_Lógica de contratos (registro informativo, sin contabilidad)._

  - `async def registrar_contrato(session)` — 
  - `async def obtener_contrato(session, contrato_id)` — 
  - `async def actualizar_enlace_documento(session, contrato_id, enlace_documento)` — 
  - `async def listar_contratos(session)` — 

  depende de: `app.core.errors`, `app.core.logging`, `app.documentos.enlace`, `app.features.contratos.models`, `app.features.terceros.service`

## `backend/app/features/facturas/models.py`
_Modelo de `factura`. Ver docs/features/facturas/spec.md §4._

  - `class TipoFactura` — 
  - `class EstadoFactura` — 
  - `class Factura` — 

  depende de: `app.core.db`

## `backend/app/features/facturas/router.py`

  - `async def crear_factura(data, db)` — 
  - `async def listar_facturas(tipo, estado, db)` — 
  - `async def obtener_factura(factura_id, db)` — 
  - `async def actualizar_enlace_documento(factura_id, data, db)` — 
  - `async def pagar_factura(factura_id, data, db)` — 

  depende de: `app.core.db`, `app.features.facturas`, `app.features.facturas.models`, `app.features.facturas.schemas`, `app.features.pagos`

## `backend/app/features/facturas/schemas.py`

  - `class FacturaCreate` — 
  - `class FacturaEnlace` — Cuerpo del PATCH: solo el enlace al PDF (puede ser null para quitarlo).
  - `class FacturaOut` — 
  - `class PagarFacturaRequest` — 

  depende de: `app.features.facturas.models`

## `backend/app/features/facturas/service.py`
_Lógica de facturas: registrar factura emitida/recibida generando el_

  - `async def registrar_factura(session)` — 
  - `async def obtener_factura(session, factura_id)` — 
  - `async def actualizar_enlace_documento(session, factura_id, enlace_documento)` — 
  - `async def listar_facturas(session)` — 

  depende de: `app.contabilidad`, `app.contabilidad.asientos`, `app.contabilidad.models`, `app.core.errors`, `app.core.logging`, `app.documentos.enlace`, `app.features.facturas.models`, `app.features.terceros.service`

## `backend/app/features/movimientos/router.py`

  - `async def crear_movimiento_manual(data, db)` — 

  depende de: `app.contabilidad.schemas`, `app.contabilidad.serializers`, `app.core.db`, `app.features.movimientos`, `app.features.movimientos.schemas`

## `backend/app/features/movimientos/schemas.py`

  - `class LineaMovimientoIn` — 
  - `class MovimientoManualCreate` — 

  depende de: `app.contabilidad.models`

## `backend/app/features/movimientos/service.py`
_Lógica de movimientos manuales (asientos oficiales con soporte / internos)._

  - `async def registrar_movimiento_manual(session)` — 

  depende de: `app.contabilidad.asientos`, `app.contabilidad.models`, `app.core.errors`, `app.core.logging`, `app.features.terceros.service`

## `backend/app/features/pagos/service.py`
_Lógica de pago/cobro de facturas. Ver docs/features/pagos/spec.md §3._

  - `async def pagar_factura(session)` — 

  depende de: `app.contabilidad`, `app.contabilidad.asientos`, `app.contabilidad.models`, `app.core.errors`, `app.core.logging`, `app.features.facturas.models`, `app.features.facturas.service`

## `backend/app/features/terceros/models.py`
_Modelo de `tercero` — clientes y proveedores. Ver docs/features/terceros/spec.md._

  - `class TipoTercero` — 
  - `class Tercero` — 

  depende de: `app.core.db`

## `backend/app/features/terceros/router.py`

  - `async def crear_tercero(data, db)` — 
  - `async def listar_terceros(tipo, db)` — 
  - `async def actualizar_enlace_rut(tercero_id, data, db)` — 

  depende de: `app.core.db`, `app.features.terceros`, `app.features.terceros.models`, `app.features.terceros.schemas`

## `backend/app/features/terceros/schemas.py`

  - `class TerceroCreate` — 
  - `class TerceroEnlace` — Cuerpo del PATCH: solo el enlace al RUT (puede ser null para quitarlo).
  - `class TerceroOut` — 

  depende de: `app.features.terceros.models`

## `backend/app/features/terceros/service.py`
_Lógica de terceros. Ver docs/features/terceros/spec.md._

  - `async def crear_tercero(session)` — 
  - `async def actualizar_enlace_rut(session, tercero_id, enlace_rut)` — 
  - `async def listar_terceros(session)` — 
  - `async def obtener_tercero(session, tercero_id)` — 

  depende de: `app.core.errors`, `app.core.logging`, `app.documentos.enlace`, `app.features.terceros.models`

## `backend/app/main.py`
_Ensamblado de la aplicación FastAPI._

  - `async def lifespan(_)` — 
  - `def create_app()` — 

  depende de: `app.contabilidad.models`, `app.contabilidad.router`, `app.core.config`, `app.core.db`, `app.core.errors`, `app.core.logging`, `app.features.contratos.router`, `app.features.facturas.router`, `app.features.movimientos.router`, `app.features.terceros.router`

## `backend/app/models.py`
_Agregador de modelos._

  depende de: `app.contabilidad.models`, `app.features.contratos.models`, `app.features.facturas.models`, `app.features.terceros.models`

## `backend/app/seed.py`
_Siembra de datos base (plan de cuentas). NO crea tablas._

  - `async def seed()` — 

  depende de: `app.contabilidad.plan_cuentas`, `app.core.db`

