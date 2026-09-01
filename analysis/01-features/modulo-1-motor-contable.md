# Módulo 1 — Motor Contable Básico

**Fecha**: 2026-09-01  
**Estado**: En diseño

## Objetivo

Un sistema (sin interfaz de chat todavía) capaz de registrar entradas y salidas de dinero de una empresa, asociadas a facturas y contratos, y consultar el estado resultante. Es el "cerebro" determinístico sobre el que después se conectan WhatsApp, IA y la app nativa.

## Por qué empezar aquí

Si el motor contable no es correcto, no importa qué tan buena sea la interfaz. WhatsApp, la IA y la app nativa son solo formas de alimentar o consultar este motor — no reemplazan la necesidad de que la lógica de negocio sea sólida desde el principio.

## Alcance de este entregable

**Sí incluye:**
- Registrar una entrada (ingreso) o salida (gasto) de dinero
- Asociar una entrada/salida a una factura (emitida o recibida)
- Registrar contratos (datos básicos: partes, objeto, valor, vigencia) — sin lógica de pagos automáticos todavía
- Consultar el balance / listado de movimientos
- Persistencia real en base de datos (no en memoria)
- Una "consignación" se modela como un tipo de entrada (movimiento de dinero que entra a una cuenta) — no es una entidad aparte en este módulo
- **Movimientos manuales**, en dos libros separados: **oficial** (exige documento de soporte, cuenta para la contabilidad real) e **interno / no oficial** (para-contabilidad — sin soporte, se rastrea aparte y no aparece en el balance oficial por defecto)

**No incluye todavía (queda para módulos siguientes):**
- WhatsApp ni ninguna interfaz de chat (Módulo 2)
- Lectura automática de documentos con IA (Módulo 3)
- Reportes e indicadores financieros elaborados (Módulo 4)
- Roles/multiusuario (una sola persona por ahora)
- Multi-empresa (una sola empresa por ahora)

## Submódulo de aprendizaje — Módulo 1

### A) Contabilidad (lo necesario para este módulo)
- Qué es un "movimiento": entrada (ingreso) vs. salida (gasto)
- Diferencia entre factura, contrato y el movimiento de dinero real — no son lo mismo: un contrato puede generar varias facturas; una factura puede pagarse en varias partes o de una vez
- Qué es una cuenta / categoría de gasto, y por qué importa para que los reportes futuros tengan sentido
- Partida simple vs. partida doble — **decidido**: partida doble real desde el inicio (el dueño ya la maneja). Detalle del modelo en `analysis/04-data-model/modulo-1-modelo-datos.md`.

### B) Técnico (lo necesario para construir esto)
- Qué es un modelo de datos / base de datos relacional, con ejemplos concretos de este proyecto (tablas: factura, contrato, movimiento)
- Qué es una API — cómo algo (por ahora el propio usuario probando, después WhatsApp) le habla al motor contable
- Qué significa "determinístico" aquí: código normal con reglas explícitas, sin IA, 100% auditable línea por línea

## Estado

- Modelo de datos definido: `analysis/04-data-model/modulo-1-modelo-datos.md`
- Stack elegido: `analysis/02-architecture/tech-stack.md`
- Diseño de API y reglas de negocio: `analysis/02-architecture/modulo-1-api-design.md`
- Implementado y probado de extremo a extremo (`backend/api_smoke_test.py`): terceros, facturas (emitidas/recibidas) con generación automática de asiento, pago/cobro de facturas, contratos, movimientos manuales (libro oficial con soporte / libro interno sin soporte), plan de cuentas, listado de asientos con filtro por libro, balance por cuenta con opción de incluir lo interno

## Próximo paso

Este entregable ya cumple el alcance definido arriba. Sigue decidir con qué se prueba en la práctica (¿el propio dueño registrando datos reales durante unos días?) antes de pasar al Módulo 2 (interfaz de WhatsApp).
