# Visión del Proyecto — El Gerente (v2)

**Fecha de pivote**: 2026-09-01  
**Estado**: En definición — pivote de alcance respecto a la v1

## Qué cambió respecto a la v1

La primera sesión de brainstorming (2026-04-10) definió una plataforma SaaS multi-tenant genérica para PYMEs, con roles operativos tipo restaurante (mesero, cocina, repartidor) y hosting inicial en Fury (MercadoLibre). Esos documentos se archivaron en `analysis/_archive/2026-04-10-v1-plataforma-multitenant/` — no se borraron porque algunas ideas (RBAC adaptativo, plan de extracción a microservicios) pueden reutilizarse más adelante, pero ya no reflejan la dirección actual del proyecto.

Se descarta el hosting en Fury por completo: ya no hay acceso a esa plataforma. Ver detalle de la decisión en `2026-09-01-sesion-inicial.md`.

## Idea central (v2)

Herramienta para gestionar la contabilidad de **una empresa propia** — no multi-tenant, al menos no en el MVP: facturas internas y externas, contratos, y consignaciones (dinero, servicios como energía, etc.). La interfaz inicial es un **chatbot de WhatsApp**, no una app web ni mobile. Más adelante, una app nativa consumible desde las App Stores.

## Principios

- **Determinística primero, IA donde aporta valor real**: la lógica de negocio (cálculos, reglas contables, flujos de registro) es código normal, determinístico y auditable. La IA se reserva para tareas que realmente la necesitan: lectura y extracción de datos de facturas, contratos y comprobantes de consignación (foto/PDF → datos estructurados).
- **Auditable por el dueño**: el dueño del proyecto no domina las herramientas técnicas involucradas. Cada decisión de arquitectura relevante debe explicarse en términos simples *antes* de implementarse, para que pueda revisarla y aprobarla — no solo confiar en que "funciona".
- **Empieza pequeño, no cierres puertas**: se construye para resolver el caso propio primero, evitando decisiones que hagan imposible ofrecerlo como producto a otras empresas más adelante (ver `_archive/.../business-model.md` para ideas de monetización que podrían retomarse).

## Capacidades clave (v2)

### Registro vía WhatsApp
- Registrar facturas (emitidas y recibidas)
- Registrar contratos
- Registrar consignaciones (dinero, servicios como energía, etc.)
- Consultar estado de cuentas / balances vía chat

### Capa IA (puntual, no central)
- Lectura de facturas (foto/PDF → datos estructurados)
- Lectura de contratos (extracción de términos clave)
- Lectura de comprobantes de consignación

### Futuro
- App nativa (App Store / Play Store) como interfaz adicional, no como reemplazo del chat
- Posible expansión a producto multi-tenant si el enfoque propio valida el modelo

## Preguntas abiertas

- ¿Qué proveedor de WhatsApp Business API se usa (Meta Cloud API directo, Twilio, otro)? — pendiente de módulo de aprendizaje.
- ¿Un solo negocio o varias empresas del mismo dueño desde el día 1?
- ¿Cómo se garantiza que las lecturas de IA (facturas/contratos) sean auditables? Propuesta a validar: guardar siempre el documento original + el dato extraído + nivel de confianza del modelo, y pedir confirmación al usuario antes de dar el dato por bueno.
- ¿Cumplimiento DIAN (factura electrónica) desde el día 1, o registro interno primero? — `analysis/04-data-model/data-requirements-research.md` sigue vigente para esto.

## Decisiones tomadas (v2)

| Decisión | Valor | Fecha |
|---|---|---|
| Interfaz inicial | Chatbot de WhatsApp | 2026-09-01 |
| Alcance inicial | Una empresa propia (no multi-tenant) | 2026-09-01 |
| Filosofía técnica | Determinística + IA puntual para lectura de documentos | 2026-09-01 |
| Hosting Fury/MercadoLibre | Descartado — sin acceso | 2026-09-01 |
| Interfaz futura | App nativa App Store / Play Store | 2026-09-01 |
| Forma de trabajo | Aprendizaje guiado: cada herramienta se explica antes de usarse | 2026-09-01 |
