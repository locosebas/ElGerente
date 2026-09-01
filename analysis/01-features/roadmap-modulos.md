# Hoja de Ruta de Módulos — El Gerente

**Fecha**: 2026-09-01  
**Estado**: Propuesta inicial — la división puede cambiar, esto es un punto de partida

## Principio de división

Cada módulo es un **entregable funcional independiente**, no una capa técnica aislada. Cada módulo incluye su propio **submódulo de aprendizaje**: antes de construir, se explican los conceptos de negocio y técnicos necesarios para ese módulo específico — no una clase teórica general, sino lo justo para entender y auditar lo que se va a construir.

Orden: de adentro hacia afuera. Primero el motor de negocio determinístico (sin el cual nada más tiene sentido), después las interfaces (WhatsApp, IA, app nativa).

## Módulos

### Módulo 1 — Motor contable básico
**Objetivo**: registrar entradas y salidas de dinero de una empresa, asociadas a facturas y contratos, con persistencia real. Sin interfaz de chat todavía — es el "cerebro" sobre el que se conecta todo lo demás.  
**Aprendizaje incluido**: conceptos contables básicos (entrada/salida, factura vs. contrato vs. movimiento, partida simple), modelo de datos relacional, qué es una API.  
**Depende de**: nada — es el punto de partida.  
**Detalle**: ver `analysis/01-features/modulo-1-motor-contable.md`

### Módulo 2 — Interfaz de WhatsApp (registro manual)
**Objetivo**: registrar movimientos, facturas y contratos escribiendo en un chat de WhatsApp, con un flujo guiado (sin IA todavía — comandos y preguntas estructuradas que llaman al motor del Módulo 1).  
**Aprendizaje incluido**: cómo funciona la WhatsApp Business Platform (Meta Cloud API vs. intermediarios como Twilio), qué es un webhook, cómo un servidor recibe y responde mensajes.  
**Depende de**: Módulo 1.

### Módulo 3 — Capa de IA para lectura de documentos
**Objetivo**: cuando el usuario envía una foto o PDF de una factura, contrato o comprobante de consignación por WhatsApp, el sistema extrae los datos automáticamente y los propone para confirmación antes de guardarlos en el motor del Módulo 1.  
**Aprendizaje incluido**: diferencia entre OCR y extracción con modelos de lenguaje, qué es un prompt, por qué siempre se guarda el documento original + el dato extraído + una confirmación humana (auditabilidad).  
**Depende de**: Módulo 1 y 2.

### Módulo 4 — Reportes y salud financiera
**Objetivo**: consultar por WhatsApp indicadores básicos — flujo de caja, gastos por categoría, facturas pendientes — calculados sobre los datos del Módulo 1.  
**Aprendizaje incluido**: indicadores financieros básicos para una empresa pequeña (los mismos que ya se investigaron en `04-data-model/data-requirements-research.md`), cómo se calculan a partir de movimientos simples.  
**Depende de**: Módulo 1 (y se enriquece con 2 y 3).

### Módulo 5 — App nativa (App Store / Play Store)
**Objetivo**: interfaz visual adicional (no reemplaza WhatsApp) que consume el mismo motor de los módulos anteriores.  
**Aprendizaje incluido**: diferencia entre app nativa, PWA y app híbrida; qué implica publicar en las tiendas.  
**Depende de**: Módulos 1–4 maduros.

### Módulo 6 (futuro, opcional) — Multi-empresa / productización
**Objetivo**: si el enfoque para una sola empresa valida el modelo, evaluar ofrecerlo a otros negocios. Retoma ideas archivadas en `analysis/_archive/2026-04-10-v1-plataforma-multitenant/` (RBAC, plan de extracción a microservicios).  
**Depende de**: validación real de los módulos 1–5 en el negocio propio.

## Convención de nombres

`analysis/01-features/modulo-N-nombre-corto.md` — un archivo de detalle por módulo, creado cuando ese módulo empieza a trabajarse activamente (no se escriben todos de antemano, para no adivinar decisiones que aún no se han tomado).
