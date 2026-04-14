# Diseño del Agente IA — El Gerente

**Fecha**: 2026-04-10  
**Estado**: Decisión tomada

## Dos modos de operación

### 1. Agente de Onboarding (al crear el negocio)
- Hace preguntas al dueño: tipo de negocio, empleados, productos, cómo vende
- Configura el sistema automáticamente: activa módulos relevantes, sugiere roles, crea categorías de inventario iniciales
- Eficiente en tokens: flujo guiado con preguntas cerradas, no conversación abierta

### 2. Agente Conversacional (siempre disponible)
- El usuario le habla en lenguaje natural: "quiero registrar las mesas de mi restaurante"
- El agente interpreta la intención y ejecuta cambios de configuración
- Limitado por el rol del usuario (ver matriz abajo)
- Principio: **ediciones pequeñas y eficientes** — minimizar costo agéntico

## Capacidades del agente por rol

| Acción del agente | Dueño | Admin | Cajero | Bodeguero | Mesero/Cocina |
|---|---|---|---|---|---|
| Reconfigurar módulos del negocio | ✅ | ❌ | ❌ | ❌ | ❌ |
| Crear/editar roles y permisos | ✅ | ❌ | ❌ | ❌ | ❌ |
| Modificar esquema de datos del negocio | ✅ | ❌ | ❌ | ❌ | ❌ |
| Crear categorías / productos en inventario | ✅ | ✅ | ❌ | ✅ | ❌ |
| Ayuda operativa (cómo registrar X) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Generar reportes bajo demanda | ✅ | ✅ | ❌ | ❌ | ❌ |
| Detectar ineficiencias y alertar | ✅ | ✅ | ❌ | ❌ | ❌ |

## Principio de eficiencia agéntica

El agente debe minimizar el costo por operación:
- Onboarding: flujo estructurado con preguntas cerradas (no LLM libre)
- Cambios de configuración: el agente propone, el usuario aprueba antes de ejecutar
- Operaciones costosas (análisis completo del negocio): solo bajo demanda explícita y en tier pago

## Stack del agente

- **Framework**: LangChain o Anthropic SDK directo (Python)
- **Modelo**: Claude (vía API Anthropic)
- **Herramientas del agente**: funciones Python que modifican la DB / configuración del negocio
- **Contexto**: cada acción del agente lleva el `user_role` y `tenant_id` — el agente no puede ejecutar acciones fuera de su scope
