# Feature: <nombre>

**Módulo**: <1 motor contable | 2 WhatsApp | 1+2>
**Código**: `backend/app/.../`
**Estado**: pendiente | en progreso | hecho y verificado

## 1. Propósito

Qué resuelve esta feature, en una o dos frases.

## 2. Alcance

**Sí incluye en v1:**
- ...

**No incluye (queda para después):**
- ...

## 3. Reglas de negocio

Numeradas, determinísticas, auditables una por una. Cada regla debe poder verificarse
leyendo el código de un solo servicio.

1. ...
2. ...

## 4. Modelo de datos

Tablas propias de esta feature (si tiene). Campos con tipo y reglas. Si no crea tablas,
decir "no crea tablas; usa las del núcleo contable".

## 5. Interfaz

### Endpoints HTTP (si aplica)

| Método | Ruta | Cuerpo / query | Respuesta |
|---|---|---|---|

### Pasos de conversación (si es un flujo de WhatsApp)

Lista ordenada de pasos: qué pregunta el bot, qué se espera, cómo se valida.

## 6. Errores

| Caso | Respuesta |
|---|---|

## 7. Casos de prueba

Cada fila se convierte en un test. `tipo` = unit o integración.

| id del test | tipo | qué verifica | archivo |
|---|---|---|---|

## 8. Notas / decisiones abiertas

Cualquier cosa por resolver o simplificación consciente que convenga dejar registrada.
