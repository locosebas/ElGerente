# Stack Tecnológico — El Gerente

**Fecha**: 2026-04-10  
**Estado**: ⚠️ En revisión — el alcance cambió el 2026-09-01 (ver `analysis/00-vision/vision.md`). Este stack se diseñó para una plataforma multi-tenant web+mobile hosteada en Fury; el MVP ahora es un chatbot de WhatsApp para una sola empresa. Se mantiene como referencia mientras se decide el stack v2.

## Stack seleccionado (v1 — bajo revisión)

| Capa | Tecnología | Justificación |
|---|---|---|
| **Backend + IA** | Python + FastAPI | Ecosistema agéntico (LangChain, Anthropic SDK, CrewAI) es Python-first. OCR, analytics y ML también. Async nativo para streaming de agentes. |
| **Frontend web** | React + Next.js (TypeScript) | Estándar de industria, gran ecosistema, SSR, comparte base con mobile. |
| **Mobile** | React Native (Expo) | Misma base React que el web — un equipo maneja los dos. Acceso a cámara para OCR de cédulas y facturas. |
| **Base de datos** | PostgreSQL | Multi-tenant via schemas. Robusto, open source, portátil entre entornos. |
| **Cache / sesiones** | Redis | Sesiones de usuario, respuestas rápidas, streams locales en dev. |
| **Archivos** | Adaptador (S3 / disco) | Fotos de facturas, documentos. Intercambiable por entorno. |

## Principio de separación

Back y front son servicios independientes. Se comunican exclusivamente via API REST (y WebSocket para actualizaciones de agentes en tiempo real).

## Por qué Python gana en backend para IA agéntica

- **LangChain, CrewAI, AutoGen, Semantic Kernel**: Python-first. Las versiones JS son ciudadanos de segunda.
- **Anthropic SDK / OpenAI SDK**: Python es la implementación canónica.
- **OCR** (lectura de cédulas/facturas): Tesseract, EasyOCR, PaddleOCR — todos Python.
- **Analytics**: pandas, scikit-learn, polars — sin equivalente en otros lenguajes.
- **Streaming de respuestas agénticas**: FastAPI soporta async/await y SSE de forma nativa.

## Alternativas descartadas

| Alternativa | Por qué se descartó |
|---|---|
| Node.js backend | Ecosistema IA débil, OCR limitado, analytics inexistente |
| Go backend | Sin ecosistema IA/ML |
| Flutter mobile | Stack completamente separado (Dart), no comparte nada con web |
| Vue + Nuxt web | Bueno, pero no comparte base con mobile |
