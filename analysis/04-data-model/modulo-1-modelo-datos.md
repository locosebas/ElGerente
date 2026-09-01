# Modelo de Datos — Módulo 1 (Motor Contable Básico)

**Fecha**: 2026-09-01  
**Estado**: Decisión tomada — partida doble real desde el inicio

## Decisión

Se descarta el enfoque de "partida simple" (una sola línea por movimiento). El motor contable implementa **partida doble real** desde el Módulo 1: cada movimiento genera un asiento con líneas débito/crédito que deben cuadrar. Razón: el dueño ya domina el concepto, y evita una migración costosa más adelante si se quiere contabilidad formal o cumplimiento DIAN.

## De la contabilidad a las tablas

- **`cuenta`** — el plan de cuentas: catálogo fijo de cuentas (Caja, Bancos, Cuentas por pagar, etc.)
- **`asiento`** — el "comprobante"/encabezado de cada movimiento contable (fecha, descripción, de dónde vino)
- **`linea_asiento`** — las líneas débito/crédito de cada asiento. Regla de validación siempre activa: **suma de débitos = suma de créditos** del mismo asiento, o se rechaza.

Factura y contrato son entidades aparte que, cuando corresponde, generan un asiento — no se mezclan con el asiento mismo. Un contrato puede generar varias facturas; una factura puede terminar en más de un asiento si se paga por partes.

## Tablas

### `cuenta` (plan de cuentas)
| Campo | Tipo | Nota |
|---|---|---|
| id | PK | |
| codigo | texto | Inspirado en el PUC colombiano (1105 Caja, 1110 Bancos, 2205 Proveedores...) para no chocar con DIAN más adelante |
| nombre | texto | |
| tipo | enum | activo / pasivo / patrimonio / ingreso / gasto |

### `asiento`
| Campo | Tipo | Nota |
|---|---|---|
| id | PK | |
| fecha | fecha | |
| descripcion | texto | |
| origen | enum + FK nullable | factura_id / contrato_id / manual |
| **libro** | enum | **oficial / interna** — ver "Libro oficial vs. libro interno" abajo |
| **documento_soporte** | texto, nullable | Referencia al documento que respalda el asiento (número de factura, ruta de archivo, o una nota). **Obligatorio si `libro = oficial`**, no aplica si `libro = interna` |
| created_at | timestamp | |

## Libro oficial vs. libro interno (para-contabilidad)

Retoma un concepto que ya había aparecido en la v1 archivada (`analysis/_archive/2026-04-10-v1-plataforma-multitenant/vision.md`, sección "para-contabilidad"): además de la contabilidad formal, hay movimientos internos/no oficiales que también hay que rastrear, pero que **no deben aparecer** cuando se calcula la contabilidad real del negocio.

- **`libro = oficial`** — todo lo que genera factura o contrato entra aquí automáticamente. También se puede registrar manualmente, pero siempre exige `documento_soporte`. Es lo que cuenta para el balance real / DIAN.
- **`libro = interna`** — movimientos que se quieren rastrear pero no tienen ni necesitan documento de respaldo (ej.: el dueño saca efectivo de la caja para algo personal, un préstamo informal). Se registran igual con partida doble (mismas cuentas, mismas reglas de cuadre) para que también sean auditables entre sí, pero quedan fuera del balance oficial por defecto.

Ambos libros comparten el mismo plan de cuentas (`cuenta`) — lo que cambia es la etiqueta `libro` del asiento, no la tabla de cuentas. Esto permite ver, si se quiere, cuánto difiere la caja "oficial" de la caja "real" (oficial + interna).

### `linea_asiento`
| Campo | Tipo | Nota |
|---|---|---|
| id | PK | |
| asiento_id | FK → asiento | |
| cuenta_id | FK → cuenta | |
| debito | decimal | 0 si no aplica |
| credito | decimal | 0 si no aplica |

### `tercero`
| Campo | Tipo | Nota |
|---|---|---|
| id | PK | |
| nombre | texto | |
| nit_cedula | texto | |
| tipo | enum | cliente / proveedor |

### `factura`
| Campo | Tipo | Nota |
|---|---|---|
| id | PK | |
| tipo | enum | emitida / recibida |
| numero | texto | |
| fecha | fecha | |
| tercero_id | FK → tercero | |
| subtotal, iva, total | decimal | |
| estado | enum | pendiente / pagada / anulada |
| asiento_id | FK → asiento, nullable | se llena al contabilizar |
| archivo_original | referencia/ruta | listo para cuando el Módulo 3 (IA) suba la foto/PDF |

### `contrato`
| Campo | Tipo | Nota |
|---|---|---|
| id | PK | |
| tercero_id | FK → tercero | |
| objeto | texto | |
| valor | decimal | |
| fecha_inicio, fecha_fin | fecha | |
| estado | enum | vigente / terminado |
| archivo_original | referencia/ruta | |

## Cómo se conectan (ejemplo)

Registrar una factura recibida genera automáticamente su `asiento` con dos `linea_asiento`:
- Débito `Gastos`
- Crédito `Cuentas por pagar`

El usuario no captura manualmente débito/crédito para el caso normal — el sistema lo deriva del tipo de factura. La partida doble queda "por debajo del capó": auditable, pero no obliga a pensar en débito/crédito cada vez que se registra algo simple.

## Plan de cuentas — adición para libro interno

Dos cuentas nuevas, pensadas principalmente para `libro = interna` (aunque nada impide usarlas también en el oficial si aplica):

| Código | Nombre | Tipo |
|---|---|---|
| 2905 | Cuentas con el dueño | Pasivo |
| 5905 | Gastos internos sin soporte | Gasto |

`2905 Cuentas con el dueño` puede quedar en saldo negativo (el dueño le debe a la empresa) o positivo (la empresa le debe al dueño) — es normal en una cuenta puente de este tipo.

## Pendiente

- Elegir lenguaje, framework y base de datos para implementar esto (ver `analysis/02-architecture/tech-stack.md`, en revisión)
- `documento_soporte` es por ahora solo texto/referencia (número de factura o nota) — cuando exista carga real de archivos (Módulo 3), se conecta a un archivo de verdad
