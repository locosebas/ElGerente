# Visión del Proyecto — El Gerente

**Fecha de inicio**: 2026-04-10  
**Estado**: En definición — sesión de brainstorming activa

## Idea central

Plataforma web + mobile para propietarios de pequeños negocios (cualquier tipo, genérico), que centraliza la administración del negocio con ayuda de IA. El dueño no necesita conocimientos contables ni técnicos.

## Objetivo real (deeper purpose)

Acumular datos estructurados de cada negocio para:
1. Detectar ineficiencias y costos ocultos en la operación
2. Llevar contabilidad formal
3. Llevar para-contabilidad (registro de transacciones internas, no formales)

## Capacidades clave identificadas

### Capa de datos / contabilidad
- **Contabilidad**: registro formal de ingresos, gastos, facturas
- **Para-contabilidad**: transacciones internas (no formales) — gastos sin factura, préstamos del dueño, etc.
- **Inventario**: control de stock
- **Análisis de ineficiencias**: cruzar datos para detectar costos ocultos, fugas

### Capa de IA / agente
- **Agente de adaptación**: puede modificar esquemas de DB y UI por tipo de negocio
- Principio: **ediciones pequeñas y eficientes** — minimizar costo agentico
- Lectura de facturas con OCR + extracción de datos
- Posiblemente: detección de anomalías en transacciones

### Plataforma
- Web (desktop) + Mobile (app o PWA)
- Genérico: cualquier negocio pequeño sin especialización vertical

## Preguntas abiertas

- ¿Quién analiza los datos para detectar ineficiencias? ¿El dueño del negocio vía dashboard, o un operador externo (quien construye el producto)?
- ¿La para-contabilidad es visible para alguien más fuera del dueño?
- ¿El agente de adaptación actúa solo o requiere aprobación del dueño?
- ¿Cuántos negocios simultáneos puede manejar un usuario?
- Stack tecnológico preferido

## Decisiones tomadas

| Decisión | Valor | Fecha |
|---|---|---|
| Plataforma | Web + Mobile | 2026-04-10 |
| Verticales | Genérico (adaptativo) | 2026-04-10 |
| Propósito profundo | Acumulación de datos → detección de ineficiencias | 2026-04-10 |
