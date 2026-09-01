# El Gerente

Herramienta para gestionar la contabilidad de una empresa (facturas, contratos, consignaciones) vía chatbot de WhatsApp, apoyada puntualmente con IA para lectura de documentos.

## Objetivo

Permitir registrar y consultar facturas internas y externas, contratos y consignaciones a través de un chat de WhatsApp, con una lógica de negocio determinística y auditable. La IA se usa solo donde aporta valor real: lectura de facturas, contratos y comprobantes de consignación. Más adelante, una app nativa (App Store / Play Store) como interfaz adicional.

## Estructura de análisis

```
analysis/
  00-vision/          # Visión general, usuarios, alcance
  01-features/        # Definición de features y módulos
  02-architecture/    # Decisiones técnicas y arquitectura
  03-ux/              # Flujos de usuario, wireframes, UX
  04-data-model/      # Modelo de datos
  05-ai-layer/        # Integración de IA (facturas, inventario, etc.)
  _archive/           # Versiones anteriores del análisis, ya no vigentes pero conservadas
docs/
  superpowers/
    specs/            # Specs detalladas por módulo
    plans/            # Planes de implementación
```

## Estado del proyecto

> En fase de brainstorming y definición — ver `analysis/00-vision/vision.md` y `analysis/00-vision/2026-09-01-sesion-inicial.md` para el pivote de alcance más reciente.
