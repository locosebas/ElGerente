# Análisis de Requerimientos de Datos — El Gerente

**Fecha**: 2026-04-10  
**Fuentes**: DIAN Colombia, NIIF PYMES, indicadores financieros INCP Colombia, best practices POS

---

## 1. Información obligatoria por ley en Colombia

| Información | Por qué es obligatoria | Entidad en el sistema |
|---|---|---|
| NIT del negocio + dígito de verificación | Requerido en toda factura electrónica DIAN (UBL 2.1) | `tenant.nit` |
| Cédula / NIT del cliente | Obligatorio en factura electrónica DIAN | `cliente.cedula_nit` |
| Fecha, subtotal, IVA, total | Libro diario + factura electrónica | `factura` |
| Descripción y cantidad de productos | Líneas de detalle obligatorias en factura | `factura_item` |
| Inventario de mercancía | Libro de inventarios y balances (obligatorio) | `producto.stock` |
| Devoluciones / notas crédito | Obligatorio DIAN al anular o devolver | `devolucion` |
| Conservación documentos 10 años | Ley colombiana — auditorías fiscales | Soft delete + archivos PDF |

**Marco legal**: Ley 1314 de 2009, NIIF PYMES, Resolución DIAN factura electrónica UBL 2.1

---

## 2. Información necesaria para salud financiera

Indicadores financieros clave para microempresas (fuente: INCP Colombia, Kleva.co):

| Indicador | Datos requeridos | Detecta |
|---|---|---|
| Flujo de caja | Todas las entradas y salidas con fecha | ¿Hay plata para el próximo mes? |
| Margen bruto | Precio de venta + costo del producto | ¿Vendo a pérdida sin saberlo? |
| Rotación de inventario | Tiempo promedio en venderse cada producto | Productos que no rotan (capital muerto) |
| Cuentas por cobrar | Ventas a crédito pendientes | Clientes que deben hace mucho |
| Gastos por categoría | Tipo de gasto: arriendo, nómina, insumos | ¿Qué gasto crece sin control? |
| Ventas por período | Ventas diarias, semanales, mensuales | Días pico, estacionalidad |

---

## 3. Información operativa (POS / día a día)

| Información | Para qué sirve | Entidad |
|---|---|---|
| Método de pago (efectivo, tarjeta, transferencia) | Cuadre de caja, conciliación bancaria | `venta.metodo_pago` |
| Proveedor de cada producto | Saber a quién pedir más stock | `proveedor` |
| Stock mínimo por producto | Alertas automáticas de reabastecimiento | `producto.stock_minimo` |
| Apertura y cierre de caja | Detectar faltantes o sobrantes | `turno_caja` |
| Historial de cambios de precio | Auditoría anti-fraude interno | `producto_precio_log` |

---

## 4. Entidades identificadas por la investigación (faltaban en el modelo inicial)

| Entidad | Campos clave | Módulo |
|---|---|---|
| `proveedor` | nit, nombre, contacto, productos | Inventario |
| `turno_caja` | apertura, cierre, saldo_inicial, saldo_final, diferencia, cajero_id | Ventas |
| `devolucion` | venta_id, motivo, monto, nota_credito_dian, estado | Ventas / Facturación |
| `gasto` | categoria, monto, fecha, proveedor_id, tiene_factura, descripcion | Para-contabilidad / Contabilidad |
| `cuenta_por_cobrar` | cliente_id, monto, fecha_vencimiento, estado | Ventas |
| `producto_precio_log` | producto_id, precio_anterior, precio_nuevo, usuario_id, fecha | Inventario / Auditoría |

---

## 5. Modelo de datos completo (v2 — post investigación)

### Schema: platform
- `tenants` — negocios registrados
- `users` — usuarios del sistema
- `roles` — roles RBAC
- `permissions` — permisos por módulo
- `subscriptions` — plan free/pro

### Schema: tenant_{id}
**Módulo Ventas**: `venta`, `venta_item`, `turno_caja`, `devolucion`, `cuenta_por_cobrar`  
**Módulo Inventario**: `producto`, `movimiento_stock`, `proveedor`, `producto_precio_log`  
**Módulo Facturación**: `factura`, `factura_item`  
**Módulo Clientes**: `cliente`  
**Módulo Pedidos**: `pedido`, `pedido_item` *(activo solo en negocios tipo restaurante)*  
**Módulo Contabilidad**: `gasto`  
**Módulo Para-contabilidad**: `transaccion_interna` *(encriptado, solo Dueño)*
