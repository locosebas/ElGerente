# Plan de Microservización — El Gerente

**Fecha**: 2026-04-10  
**Estado**: Documento vivo — actualizar cuando cambien las condiciones de carga

## Decisión de arquitectura inicial

**Opción C**: Monolito modular + servicio de agente IA separado.  
El monolito se diseña con límites estrictos desde el día 1 para que cualquier módulo sea extraíble sin cirugía.

## Reglas de diseño que hacen posible la migración

Estas reglas deben respetarse en todo momento dentro del monolito:

1. **Un módulo nunca llama directamente al modelo de otro módulo** — solo a su `service.py`
2. **Cada módulo tiene su propio schema en PostgreSQL** — sin tablas compartidas entre módulos
3. **Comunicación entre módulos vía interfaces** — no imports cruzados de modelos ORM
4. **Sin lógica de negocio en los routers** — la lógica vive en `service.py`, que es lo que se extrae

## Módulos del monolito (candidatos a extracción)

| Módulo | Schema DB | Se extrae cuando... | Prioridad |
|---|---|---|---|
| `ventas` | `tenant_{id}.ventas` | Alto volumen de transacciones simultáneas | Alta |
| `inventario` | `tenant_{id}.inventario` | Operaciones de bodega frecuentes e independientes | Media |
| `facturacion` | `tenant_{id}.facturacion` | Volumen alto + integración DIAN requiere aislamiento | Alta |
| `pedidos` | `tenant_{id}.pedidos` | Restaurantes con muchas mesas concurrentes | Media |
| `reportes` | (solo lectura, replica) | Analytics pesados afectan performance del monolito | Alta |
| `auth` / `rbac` | `platform.auth` | Siempre disponible incluso si el monolito está caído | Alta |

## Servicios separados desde el inicio

Estos **nunca** viven en el monolito:

| Servicio | Razón |
|---|---|
| `api-agente` | Perfil de carga diferente: lento, costoso, bloqueable |
| `api-analytics` | Queries pesados no deben competir con operaciones de caja |

## Proceso de extracción (paso a paso por módulo)

```
Paso 1 — Verificar límites
  └─ El módulo no tiene imports directos de otros módulos
  └─ Tiene su propio schema en DB

Paso 2 — Crear nuevo repo
  └─ Copiar módulo: service.py + models.py + router.py
  └─ Agregar Dockerfile + config ENV

Paso 3 — Desplegar en paralelo
  └─ El nuevo servicio corre junto al monolito
  └─ El monolito sigue siendo la fuente de verdad

Paso 4 — Migrar tráfico gradualmente
  └─ Feature flag: X% del tráfico va al nuevo servicio
  └─ Monitorear errores y latencia

Paso 5 — Cortar el monolito
  └─ Reemplazar llamadas internas por HTTP al nuevo servicio
  └─ Eliminar el módulo del monolito

Paso 6 — Migrar DB schema (si aplica)
  └─ Mover schema a instancia propia de PostgreSQL
  └─ Actualizar connection string vía ENV
```

## Señales de que es momento de extraer un módulo

- El módulo representa >30% del tiempo de respuesta del monolito
- Una falla en el módulo afecta operaciones críticas (caja, ventas)
- El módulo necesita escalar a un ritmo diferente al resto
- El módulo requiere una tecnología diferente (ej: analytics → columnar DB)

## Estado actual de microservización

| Componente | Estado | Fecha estimada extracción |
|---|---|---|
| Monolito principal | ✅ En construcción | — |
| `api-agente` | ✅ Separado desde inicio | — |
| `api-analytics` | ✅ Separado desde inicio | — |
| `ventas` → microservicio | ⏳ Pendiente | Cuando haya >50 negocios activos |
| `facturacion` → microservicio | ⏳ Pendiente | Cuando se active DIAN compliance |
| `auth/rbac` → microservicio | ⏳ Pendiente | Antes de lanzar público |
