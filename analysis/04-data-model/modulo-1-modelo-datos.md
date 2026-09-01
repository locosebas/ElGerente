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
| created_at | timestamp | |

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

## Pendiente

- Definir el plan de cuentas inicial completo (subconjunto mínimo de cuentas para arrancar)
- Elegir lenguaje, framework y base de datos para implementar esto (ver `analysis/02-architecture/tech-stack.md`, en revisión)
