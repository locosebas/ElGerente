# Feature: terceros

**Módulo**: 1 — motor contable
**Código**: `backend/app/features/terceros/`
**Estado**: hecho y verificado (56 tests en verde)

## 1. Propósito

Registrar y listar a las personas o empresas con las que se hacen operaciones: **clientes**
(a quienes se les emite factura) y **proveedores** (de quienes se recibe factura). Una
factura o un contrato siempre apunta a un tercero.

## 2. Alcance

**Sí incluye en v1:**
- Crear un tercero (`nombre`, `nit_cedula`, `tipo`).
- Listar todos los terceros.

**No incluye:**
- Editar o borrar terceros.
- Datos de contacto (teléfono, email, dirección).
- Validación del dígito de verificación del NIT.
- Distinguir "es cliente y proveedor a la vez" (hoy es uno u otro).

## 3. Reglas de negocio

1. `tipo` es `cliente` o `proveedor`, obligatorio.
2. `nombre` y `nit_cedula` son texto obligatorio. No se valida formato del NIT en v1 (se
   guarda tal cual se recibe).
3. No hay unicidad forzada sobre `nit_cedula` en v1 (se puede registrar dos veces el mismo
   por error; se acepta para no bloquear el registro rápido — ver §8).

## 4. Modelo de datos

### `tercero`

| Campo | Tipo | Reglas |
|---|---|---|
| `id` | int, PK | |
| `nombre` | str(150) | obligatorio |
| `nit_cedula` | str(20) | obligatorio |
| `tipo` | enum `TipoTercero` | `cliente` \| `proveedor` |
| `enlace_rut` | str(500), nullable | URL al RUT — ver [`documentos/spec.md`](../documentos/spec.md) |

## 5. Interfaz

| Método | Ruta | Cuerpo / query | Respuesta |
|---|---|---|---|
| `POST` | `/terceros` | `{ "nombre": "...", "nit_cedula": "...", "tipo": "cliente" }` | `TerceroOut` (200) |
| `GET` | `/terceros` | `tipo` opcional (`cliente`\|`proveedor`) | `TerceroOut[]` |

`TerceroOut`: `{ "id": 1, "nombre": "...", "nit_cedula": "...", "tipo": "cliente" }`

## 6. Errores

| Caso | Respuesta |
|---|---|
| Falta un campo o `tipo` inválido | `422` (Pydantic) |

## 7. Casos de prueba

| id del test | tipo | qué verifica | archivo |
|---|---|---|---|
| `test_crear_tercero_devuelve_id` | unit | el servicio persiste y devuelve el tercero con id | `tests/unit/terceros/test_service.py` |
| `test_listar_terceros_filtra_por_tipo` | unit | `listar(tipo="cliente")` no trae proveedores | `tests/unit/terceros/test_service.py` |
| `test_post_terceros_ok` | integración | `POST /terceros` → 200 y aparece en `GET /terceros` | `tests/integration/test_terceros.py` |
| `test_post_terceros_tipo_invalido` | integración | `tipo="otro"` → 422 | `tests/integration/test_terceros.py` |

## 8. Notas / decisiones abiertas

- **Unicidad del NIT:** pendiente de decidir si se fuerza (índice único) o se deja como
  advertencia. En v1 se deja libre para no frenar el registro; cuando exista la interfaz de
  WhatsApp conviene, como mínimo, avisar "ya existe un tercero con ese NIT, ¿es el mismo?".
- Editar/borrar terceros y agregar contacto quedan para cuando haga falta.
