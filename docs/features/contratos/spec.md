# Feature: contratos

**Módulo**: 1 — motor contable
**Código**: `backend/app/features/contratos/`
**Estado**: hecho y verificado (56 tests en verde)

## 1. Propósito

Registrar los datos básicos de un contrato con un tercero (objeto, valor, vigencia) para
tenerlos a mano. En v1 es un **registro informativo**: no genera asientos ni programa pagos
automáticos.

## 2. Alcance

**Sí incluye en v1:**
- Crear un contrato (`tercero`, `objeto`, `valor`, `fecha_inicio`, `fecha_fin` opcional).
- Listar contratos.

**No incluye:**
- Generar facturas o asientos a partir del contrato.
- Cronograma de pagos / cuotas.
- Alertas de vencimiento.
- Cambiar el estado (`vigente`/`terminado`) por API — nace `vigente`.
- Subir el archivo del contrato (hoy solo un **enlace** — ver
  [`documentos/spec.md`](../documentos/spec.md)).

## 3. Reglas de negocio

1. **El tercero debe existir** → si no, `NoEncontrado` (404).
2. `valor` ≥ 0.
3. Si se da `fecha_fin`, debe ser ≥ `fecha_inicio`.
4. El contrato nace en estado `vigente`.
5. **No toca la contabilidad.** Un contrato puede, más adelante, generar varias facturas
   —pero eso es registrar cada factura por separado en la feature `facturas`.

## 4. Modelo de datos

### `contrato`

| Campo | Tipo | Reglas |
|---|---|---|
| `id` | int, PK | |
| `tercero_id` | FK → `tercero.id` | debe existir |
| `objeto` | text | descripción de qué cubre el contrato |
| `valor` | Numeric(14,2) | ≥ 0 |
| `fecha_inicio` | date | |
| `fecha_fin` | date, nullable | ≥ `fecha_inicio` si se da |
| `estado` | enum `EstadoContrato` | `vigente` \| `terminado`; nace `vigente` |
| `enlace_documento` | str(500), nullable | URL al PDF del contrato — ver [`documentos/spec.md`](../documentos/spec.md) |

## 5. Interfaz

| Método | Ruta | Cuerpo / query | Respuesta |
|---|---|---|---|
| `POST` | `/contratos` | `{ "tercero_id": 1, "objeto": "Arrendamiento bodega", "valor": "2000000", "fecha_inicio": "2026-09-01", "fecha_fin": "2027-09-01" }` | `ContratoOut` (200) |
| `GET` | `/contratos` | — | `ContratoOut[]` |

## 6. Errores

| Caso | Respuesta |
|---|---|
| `tercero_id` no existe | `404` |
| `fecha_fin` < `fecha_inicio` | `422` |
| Falta un campo / tipo inválido | `422` (Pydantic) |

## 7. Casos de prueba

| id del test | tipo | qué verifica | archivo |
|---|---|---|---|
| `test_crear_contrato_ok` | unit | persiste, nace `vigente`, devuelve id | `tests/unit/contratos/test_service.py` |
| `test_contrato_tercero_inexistente` | unit | `NoEncontrado` | `tests/unit/contratos/test_service.py` |
| `test_contrato_fecha_fin_antes_de_inicio` | unit | `DatosInvalidos` | `tests/unit/contratos/test_service.py` |
| `test_contrato_no_genera_asiento` | unit | tras crear un contrato, `GET /asientos` sigue vacío | `tests/unit/contratos/test_service.py` |
| `test_post_contrato_end_to_end` | integración | `POST /contratos` → 200 y aparece en `GET /contratos` | `tests/integration/test_contratos.py` |
| `test_post_contrato_tercero_inexistente_404` | integración | `tercero_id=9999` → 404 | `tests/integration/test_contratos.py` |

## 8. Notas / decisiones abiertas

- El contrato como generador de facturas/cuotas es una feature futura (posiblemente Módulo
  4 o un módulo propio). En v1 se registra para no perder el dato.
