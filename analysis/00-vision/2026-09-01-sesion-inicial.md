# Sesión Inicial — Pivote a WhatsApp + Aprendizaje Guiado

**Fecha**: 2026-09-01

## Contexto

El repositorio `El Gerente` ya existía, con una sesión de brainstorming previa (2026-04-10) enfocada en una plataforma multi-tenant para PYMEs, pensada para hostearse en Fury (MercadoLibre). El dueño no recordaba que el repo ya existía y llegó con una idea más específica y distinta en varios aspectos clave.

## Motivación del dueño

- Quiere una aplicación para gestionar las facturas internas y externas de su empresa.
- Interfaz inicial: chatbot de WhatsApp, antes de invertir en apps de App Store.
- Casos de uso principales: registrar consignaciones, contratos y facturas — llevar la contabilidad completa a través del chat.
- Filosofía: aplicación **determinística**, con herramientas de IA usadas puntualmente — sobre todo para la lectura de facturas, contratos y comprobantes de consignación (energía, dinero, etc.).
- Se reconoce como principiante en el tema técnico: pide que el proceso sea también un **aprendizaje guiado** de arquitectura y herramientas. No busca que Claude simplemente ejecute — busca entender qué se hace y con qué herramientas, para poder auditar el trabajo por su cuenta.

## Decisiones tomadas en esta sesión

| Decisión | Detalle |
|---|---|
| Se descarta Fury/MercadoLibre | Ya no hay acceso a esa plataforma. Se eliminó `analysis/02-architecture/portability-fury.md` y se limpiaron las referencias en `tech-stack.md`. |
| No había código que borrar | El repositorio solo contenía documentos de análisis — nada que limpiar en ese frente. |
| Alcance v2 | Empieza como herramienta para la propia empresa del dueño, con arquitectura que no cierre la puerta a ofrecerlo como producto a otros negocios más adelante. |
| Documentos v1 archivados, no borrados | `vision.md`, `business-model.md`, `roles-permissions.md` y `microservices-migration-plan.md` originales se movieron a `analysis/_archive/2026-04-10-v1-plataforma-multitenant/`. Parte de ese pensamiento (RBAC, plan de extracción a microservicios) puede reutilizarse cuando el proyecto crezca. |
| Documentos que siguen vigentes | `market.md` (contexto fiscal de Colombia/DIAN) y `data-requirements-research.md` (requisitos legales de facturación electrónica) aplican directo al nuevo enfoque y no se tocaron. |

## Compromiso de forma de trabajo

Como el dueño no puede auditar por sí mismo herramientas que no conoce, el proceso de aquí en adelante debe:

1. Explicar, en lenguaje simple, qué herramienta o técnica se va a usar y por qué, **antes** de implementarla.
2. Avanzar en pasos pequeños y revisables, no en decisiones grandes de una sola vez.
3. Dejar todo documentado en `analysis/` para que la conversación no se pierda entre sesiones.

## Próximos pasos propuestos

1. **Módulo de aprendizaje 1** — ¿Qué es un chatbot de WhatsApp, técnicamente? Comparar WhatsApp Business Platform (Meta Cloud API) directo vs. proveedores intermediarios (Twilio, etc.): qué hace cada uno, costos, límites y por qué se elige uno u otro.
2. **Módulo de aprendizaje 2** — Determinístico vs. IA: dónde traza la línea el sistema entre reglas de negocio en código normal y extracción de datos de documentos con modelos de lenguaje / OCR, y cómo se audita cada lectura de IA.
3. Definir el modelo de datos mínimo del MVP: facturas, contratos, consignaciones.
4. Revisar y actualizar `tech-stack.md` para el nuevo alcance — el stack v1 se pensó para multi-tenant + Fury y ya no aplica tal cual.
