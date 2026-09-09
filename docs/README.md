# Documentación de El Gerente

Esta carpeta describe **cómo está construido el programa**, parte por parte. Es la
documentación viva: si el código cambia, esto cambia con él.

> ¿Buscas el historial de decisiones, brainstorming y visión del negocio? Eso vive en
> [`../analysis/`](../analysis/) y no se toca — es el registro de *por qué* se decidió lo
> que se decidió. `docs/` es el *qué* y el *cómo* del programa que existe hoy.

## Cómo está organizada

| Carpeta | Qué contiene |
|---|---|
| [`arquitectura/`](arquitectura/) | Las decisiones técnicas transversales: capas, por qué async, base de datos y migraciones, testing, resiliencia y logs, despliegue con Docker |
| [`aprendizaje/`](aprendizaje/) | "Submódulos de aprendizaje": explicaciones en lenguaje simple de cada concepto o herramienta *antes* de usarla, para que el dueño pueda auditar el trabajo |
| [`features/`](features/) | Una carpeta por **feature** (parte funcional del programa), cada una con su `spec.md`. Más el [índice](features/README.md) y el [catálogo de pruebas](features/pruebas.md) |

**➡ [`ESTADO.md`](ESTADO.md) — qué está hecho y qué falta, de un vistazo.**
**➡ [`MAPA.md`](MAPA.md) — navegación del código para mantenimiento (qué archivo tocar para cada cambio).**

## Regla de trabajo: plan → documentación → código

Para cada feature, en este orden y sin saltarse pasos:

1. Se escribe `features/<feature>/spec.md` completo (usando la [plantilla](features/_PLANTILLA-spec.md)).
2. Se implementa la carpeta de código correspondiente.
3. Se escriben los tests de la sección "Casos de prueba" del spec hasta que pasen.
4. Se marca el estado en el `spec.md` y en el [índice de features](features/README.md).

## Estado general

- **Módulo 1 — motor contable**: ✅ completo, arquitectura por features, 56 tests en verde
  (ver [`features/README.md`](features/README.md)).
- **Módulo 2 — WhatsApp**: ⬜ pendiente (chatbot 100 % determinístico — ver
  [`aprendizaje/deterministico-vs-ia.md`](aprendizaje/deterministico-vs-ia.md)).
- **Interfaz gráfica HTML**: ⬜ pendiente.
- El roadmap completo de módulos está en
  [`../analysis/01-features/roadmap-modulos.md`](../analysis/01-features/roadmap-modulos.md).
