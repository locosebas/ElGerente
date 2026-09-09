# Determinístico vs. IA — dónde traza la línea El Gerente

## Las dos formas de que un programa "decida" algo

| | Código determinístico | Modelo de lenguaje / IA |
|---|---|---|
| Cómo decide | Reglas explícitas escritas por una persona (`if`, tablas, cálculos) | Predice la respuesta más probable a partir de ejemplos que vio en su entrenamiento |
| Mismo input, ¿mismo output? | **Siempre** | No necesariamente |
| ¿Se puede auditar leyendo el código? | **Sí**, línea por línea | No: es una caja donde entra texto y sale texto |
| Cuándo conviene | Reglas de negocio, cálculos, flujos | Entender lenguaje natural desordenado, leer un documento escaneado |

## La regla del proyecto

> **La lógica de negocio es determinística. La IA se reserva para tareas que de verdad la
> necesitan: leer y extraer datos de documentos (facturas, contratos, comprobantes).**

Esto viene de la visión (`analysis/00-vision/vision.md`): el dueño necesita poder **auditar**
lo que el sistema hace con su plata. Un cálculo contable que "a veces da distinto" no es
aceptable.

## Qué es determinístico (todo el motor y todo el chat)

- **Módulo 1 — motor contable:** 100 % código normal. Las reglas de generación de asientos
  son tablas fijas (ver los specs de `facturas` y `pagos`). Dada una factura, siempre sale
  el mismo asiento.
- **Módulo 2 — chatbot de WhatsApp:** **100 % determinístico también.** Decisión explícita
  del dueño. Esto incluye:
  - los **flujos de registro** (factura, pago, contrato, movimiento): máquinas de estado
    con pasos y validaciones fijas;
  - el **asistente de uso** (`whatsapp-asistente`): saludo, menú, `ayuda`, `cancelar`,
    fallback "no entendí" — todo con textos fijos;
  - la **detección de intención**: por palabras clave (`"factura"` → flujo de factura), no
    por interpretación de un modelo.

  Si el usuario escribe algo que el chatbot no reconoce, responde con el menú de opciones,
  no intenta "adivinar" con IA.

## Qué usará IA (más adelante, Módulo 3)

Solo una cosa: cuando el usuario mande una **foto o PDF** de una factura, contrato o
comprobante, un modelo extrae los datos (número, fecha, montos...) y los **propone** en el
flujo determinístico, que le pide al usuario que confirme antes de guardar. Siempre se
guarda: documento original + dato extraído + confirmación humana.

La IA nunca decide un asiento ni ejecuta un registro por su cuenta.

## Por qué el chatbot no usa IA en v1

- **Auditabilidad:** el dueño puede leer exactamente qué responde el bot en cada caso.
- **Costo y dependencia:** no hay que pagar por llamada ni depender de una API externa para
  que el chat funcione.
- **Previsibilidad:** un flujo guiado con preguntas cerradas es más difícil de romper que
  una conversación abierta.
- La puerta a un asistente con IA que *explique* (nunca que ejecute) queda abierta para el
  futuro, pero no entra en la primera versión.
