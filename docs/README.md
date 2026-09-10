# Documentación de El Gerente

Esta carpeta describe **cómo está construido el programa**, parte por parte. Es la
documentación viva: si el código cambia, esto cambia con él.

> ¿Buscas el historial de decisiones, brainstorming y visión del negocio? Eso vive en
> [`../analysis/`](../analysis/) y no se toca — es el registro de *por qué* se decidió lo
> que se decidió. `docs/` es el *qué* y el *cómo* del programa que existe hoy.

## Cómo está organizada

| Carpeta | Qué contiene |
|---|---|
| [`arquitectura/`](arquitectura/) | Decisiones técnicas transversales + la [vista general HTML](arquitectura/vista-general.html): capas, por qué async, base de datos, testing, resiliencia, despliegue |
| [`aprendizaje/`](aprendizaje/) | "Submódulos de aprendizaje": explicaciones en lenguaje simple de cada concepto o herramienta *antes* de usarla, para que el dueño pueda auditar el trabajo |
| [`features/`](features/) | Una carpeta por **feature** (parte funcional del programa), cada una con su `spec.md`. Más el [índice](features/README.md) y el [catálogo de pruebas](features/pruebas.md) |

## Los cuatro documentos de arranque

| Documento | Para qué |
|---|---|
| **[`ESTADO.md`](ESTADO.md)** | Qué está hecho y qué falta, cómo correr y probar. Lo primero a leer. |
| **[`MAPA.md`](MAPA.md)** | "Quiero cambiar X → qué archivo y qué símbolo tocar" + reglas de arquitectura + grafo de dependencias. |
| **[`TAREAS.md`](TAREAS.md)** | Backlog priorizado; cada tarea sirve como un chat / un agente. |
| **[`PARA-NUEVO-CHAT.md`](PARA-NUEVO-CHAT.md)** | Prompts de arranque, cómo dividir el trabajo en varios chats sin pisarse, checklist de cierre. |

Y la arquitectura de un vistazo: [`arquitectura/vista-general.html`](arquitectura/vista-general.html).

## Regla de trabajo: plan → documentación → código

Para cada feature, en este orden y sin saltarse pasos:

1. Se escribe `features/<feature>/spec.md` completo (usando la [plantilla](features/_PLANTILLA-spec.md)).
2. Se implementa la carpeta de código correspondiente.
3. Se escriben los tests de la sección "Casos de prueba" del spec hasta que pasen.
4. Se marca el estado en el `spec.md` y en el [índice de features](features/README.md).

## Estado general

- **Módulo 1 — motor contable** + interfaz gráfica + endurecimiento: ✅ completo, 90 tests
  en verde (ver [`ESTADO.md`](ESTADO.md) y [`features/README.md`](features/README.md)).
- **Módulo 2 — WhatsApp**: ⬜ pendiente (chatbot 100 % determinístico — ver
  [`aprendizaje/deterministico-vs-ia.md`](aprendizaje/deterministico-vs-ia.md) y `TAREAS.md`).
- El roadmap completo de módulos está en
  [`../analysis/01-features/roadmap-modulos.md`](../analysis/01-features/roadmap-modulos.md).
