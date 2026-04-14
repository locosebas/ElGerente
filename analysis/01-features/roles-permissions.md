# Roles y Permisos — El Gerente

**Fecha**: 2026-04-10  
**Estado**: Decisión tomada

## Sistema: RBAC Adaptativo

El dueño puede crear roles personalizados y elegir a qué módulos tiene acceso cada uno, con qué nivel.

### Niveles de acceso por módulo
- **Acceso completo** — puede leer y modificar
- **Solo lectura** — puede ver pero no modificar
- **Sin acceso** — el módulo no aparece en la interfaz

### Roles predefinidos (plantillas de inicio)

| Rol | Descripción |
|---|---|
| 👑 **Dueño** | Acceso total. Único con acceso a para-contabilidad personal. |
| 🧑‍💼 **Administrador** | Casi todo excepto para-contabilidad del dueño. Gestiona empleados. |
| 🧾 **Cajero** | Ventas, cobros, apertura/cierre de caja, generación de facturas. |
| 📦 **Bodeguero** | Inventario: entradas, salidas, conteo, recepción de pedidos. |
| 🍽️ **Mesero** | Toma pedidos por mesa, envía a cocina, ve estado de sus mesas. |
| 👨‍🍳 **Cocina** | Ve pedidos entrantes, marca como listos. Sin caja ni inventario. |
| 🛵 **Repartidor** | Ve pedidos asignados, marca como entregados. Vista móvil. |
| 📊 **Contador externo** | Solo lectura: reportes y exportación contable. |

### Matriz de permisos base

| Módulo | Dueño | Admin | Cajero | Bodeguero | Mesero | Cocina | Repartidor | Contador |
|---|---|---|---|---|---|---|---|---|
| Ventas / Caja | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | 👁️ |
| Inventario | ✅ | ✅ | 👁️ | ✅ | ❌ | ❌ | ❌ | 👁️ |
| Facturación | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | 👁️ |
| Pedidos | ✅ | ✅ | ✅ | 👁️ | ✅ | 👁️ | 👁️ | ❌ |
| Para-contabilidad | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Reportes / Analytics | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | 👁️ |
| Configuración del negocio | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Gestión de empleados | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

## Regla especial: Para-contabilidad

La para-contabilidad es **exclusiva del Dueño**. Ningún rol puede tener acceso a ella, ni siquiera el Administrador. No es configurable en el RBAC.

## Flujo de creación de rol personalizado

1. Dueño va a Configuración → Roles
2. Crea un nuevo rol con nombre libre (ej: "Vendedor de mostrador")
3. Para cada módulo, elige el nivel de acceso
4. Asigna el rol a uno o más empleados

## Integración con el agente IA

El agente puede sugerir roles predefinidos según el tipo de negocio que el dueño configure en el onboarding (ej: si es restaurante, sugiere Mesero + Cocina; si es tienda, sugiere Cajero + Bodeguero).

## Fuentes de investigación

- Alegra (Colombia): roles Administrador, Contador, Vendedor, Asistente
- Operación real de restaurantes LATAM: mesero, cocina, bodeguero, repartidor
- Gap identificado: ningún software colombiano actual ofrece RBAC adaptativo con esta granularidad
