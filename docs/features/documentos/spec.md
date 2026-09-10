# Feature: documentos

**Módulo**: 1 — motor contable (transversal a varias features)
**Código**: `backend/app/documentos/` + campos en `terceros`, `facturas`, `contratos`
**Estado**: en progreso

## 1. Propósito

Guardar, junto a un tercero / factura / contrato, **un enlace al documento** que lo
respalda (el RUT del tercero, el PDF de la factura, el PDF del contrato firmado).

En v1 es literalmente **una línea de texto** donde se pega una URL — normalmente un enlace
compartido de Google Drive. El objetivo es no perder de vista dónde está el papel, sin
montar todavía almacenamiento de archivos.

## 2. Alcance

**Sí incluye en v1:**
- Un campo de enlace por entidad:
  - `tercero.enlace_rut`
  - `factura.enlace_documento`
  - `contrato.enlace_documento`
- Se puede poner al crear el registro **o después** (el PDF suele llegar más tarde): hay un
  `PATCH` por entidad que solo actualiza el enlace.
- Validación básica del enlace (que sea una URL `http(s)` y no exceda 500 caracteres).
- En la interfaz: un input en cada formulario y, en las tablas, el enlace como link
  clickeable (se abre en otra pestaña).

**No incluye (queda para después):**
- Subir el archivo de verdad. Hoy solo se guarda la URL; el archivo vive en Drive (o donde
  sea) y el enlace apunta ahí.
- Varios documentos por entidad (hoy es uno). Si hace falta, se crea una tabla `documento`.
- Control de acceso al documento (lo maneja quien comparte el enlace de Drive).
- Que el enlace sea alcanzable/válido de verdad (no se hace una petición para comprobarlo).

## 3. Reglas de negocio

1. El enlace es **opcional** en los tres casos.
2. Si se envía, se recorta (`strip`) y debe:
   - empezar por `http://` o `https://`;
   - tener 500 caracteres o menos.
   Si no cumple → `DatosInvalidos` (422).
3. Un enlace vacío o solo espacios se guarda como `NULL` (equivale a "sin documento").
4. Toda la lógica del enlace vive en **`app/documentos/enlace.py`** (`validar_enlace`). Es el
   único punto que sabe qué es un "enlace de documento" — cuando se pase a S3, ahí se
   cambia (ver §8).

## 4. Modelo de datos

Migración `0002_enlaces_documentos`:

| Tabla | Campo nuevo / cambio | Tipo |
|---|---|---|
| `tercero` | `enlace_rut` (nuevo) | `String(500)`, nullable |
| `factura` | `archivo_original` → **renombrado a** `enlace_documento` | `String(500)`, nullable |
| `contrato` | `archivo_original` → **renombrado a** `enlace_documento` | `String(500)`, nullable |

> `archivo_original` estaba reservado desde el diseño original para "cuando el Módulo 3 (IA)
> suba la foto/PDF". Como nunca se usó y ahora el concepto es "enlace al documento", se
> renombra. Cuando llegue el almacenamiento real, `enlace_documento` puede pasar a contener
> una referencia interna en vez de una URL de Drive, sin cambiar el nombre.

## 5. Interfaz

### Endpoints

| Método | Ruta | Cuerpo | Efecto |
|---|---|---|---|
| `POST` | `/terceros` | `+ "enlace_rut": "https://..."` (opcional) | crea el tercero con su enlace |
| `PATCH` | `/terceros/{id}` | `{ "enlace_rut": "https://..." }` (o `null` para quitarlo) | actualiza solo el enlace |
| `POST` | `/facturas` | `+ "enlace_documento": "https://..."` (opcional) | |
| `PATCH` | `/facturas/{id}` | `{ "enlace_documento": "..." }` | |
| `POST` | `/contratos` | `+ "enlace_documento": "https://..."` (opcional) | |
| `PATCH` | `/contratos/{id}` | `{ "enlace_documento": "..." }` | |

Los esquemas `TerceroOut`, `FacturaOut` y `ContratoOut` incluyen el campo de enlace.

### Interfaz gráfica

- **Terceros / Facturas / Contratos**: el formulario de alta tiene un campo
  "Enlace al RUT / documento (Drive)".
- En cada tabla, si hay enlace, se muestra un ícono/enlace 📎 que abre el documento en otra
  pestaña; si no, un guión.
- (Editar el enlace de un registro ya creado desde la interfaz: pendiente — por ahora se
  hace por el `PATCH` de la API. Ver §8.)

## 6. Errores

| Caso | Respuesta |
|---|---|
| Enlace que no empieza por `http://` / `https://` | `422` — "El enlace debe empezar por http:// o https://" |
| Enlace de más de 500 caracteres | `422` |
| `PATCH` sobre un id que no existe | `404` |

## 7. Casos de prueba

| id del test | tipo | qué verifica | archivo |
|---|---|---|---|
| `test_validar_enlace_acepta_https` | unit | `https://drive.google.com/...` → se guarda tal cual (con `strip`) | `tests/unit/documentos/test_enlace.py` |
| `test_validar_enlace_vacio_es_none` | unit | `""` / `"   "` / `None` → `None` | `tests/unit/documentos/test_enlace.py` |
| `test_validar_enlace_rechaza_no_url` | unit | `"drive.google.com/x"` (sin esquema) → `DatosInvalidos` | `tests/unit/documentos/test_enlace.py` |
| `test_validar_enlace_rechaza_muy_largo` | unit | > 500 chars → `DatosInvalidos` | `tests/unit/documentos/test_enlace.py` |
| `test_crear_tercero_con_enlace_rut` | integración | `POST /terceros` con `enlace_rut` → aparece en `GET /terceros` | `tests/integration/test_documentos.py` |
| `test_patch_factura_enlace` | integración | `PATCH /facturas/{id}` pone el enlace; `GET` lo devuelve | `tests/integration/test_documentos.py` |
| `test_patch_contrato_quitar_enlace` | integración | `PATCH` con `null` deja el enlace en `None` | `tests/integration/test_documentos.py` |
| `test_post_factura_enlace_invalido_422` | integración | enlace sin esquema → 422 | `tests/integration/test_documentos.py` |
| `test_patch_tercero_inexistente_404` | integración | `PATCH /terceros/9999` → 404 | `tests/integration/test_documentos.py` |

## 8. Notas / decisiones abiertas

- **Futuro: almacenamiento real (S3 o similar).** Cuando se quiera guardar los archivos
  dentro del sistema en vez de depender de Drive:
  1. se agrega un adaptador `app/documentos/almacenamiento.py` con una interfaz tipo
     `subir(archivo) -> referencia` / `url_de(referencia) -> str`, con implementaciones
     `S3`, `disco local`, `fake` (para tests) — mismo patrón que el proveedor de WhatsApp;
  2. `enlace_documento` pasa a poder contener una referencia interna, y la interfaz sube el
     archivo en vez de pedir una URL;
  3. probablemente convenga entonces una tabla `documento` (varios por entidad, con tipo,
     fecha de subida, tamaño).
  Nada de esto rompe lo de v1: el campo y su validación ya están aislados en
  `app/documentos/enlace.py`.
- **Editar el enlace desde la interfaz gráfica**: falta. Hoy se hace con el `PATCH` de la
  API (o desde `/docs`). Se agrega cuando moleste.
