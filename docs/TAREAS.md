# Tareas pendientes — El Gerente

Backlog priorizado. Cada tarea está pensada para hacerse en **un chat / un agente**:
dice qué tocar, qué spec leer, cómo saber que quedó lista, y si hace falta una decisión
del dueño antes de arrancar.

Estado global y qué existe: [`ESTADO.md`](ESTADO.md). Cómo empezar un chat sin recargar
contexto: [`PARA-NUEVO-CHAT.md`](PARA-NUEVO-CHAT.md).

Leyenda: 🔴 bloquea el uso real · 🟡 mejora importante · 🟢 futuro / no urgente
· 👤 necesita una decisión del dueño primero

---

## A. Antes de exponerlo fuera de una red de confianza

### A1 🔴 Autenticación / login
Hoy no hay ningún control de acceso: cualquiera que llegue a la URL entra.
- **Decisión 👤**: ¿login simple de una sola cuenta (usuario/clave en `.env`), o algo con
  usuarios en base de datos? Para el MVP de una empresa, lo primero alcanza.
- **Dónde**: nueva feature `auth` (`app/features/auth/`), un middleware o dependencia en
  `app/main.py`, y un formulario de login en `app/web/`.
- **Listo cuando**: sin sesión válida, todo `/` y la API responden `401`; con sesión, todo
  funciona igual; hay tests de integración de ambos casos.
- Ver `docs/arquitectura/despliegue.md` ("Qué falta para clientes de verdad").

### A2 🟡 Verificar la imagen Docker
El `Dockerfile` y `docker-compose.yml` están escritos y revisados pero **nunca se
construyeron** (este entorno no tenía permisos de Docker).
- **Listo cuando**: `docker compose --env-file .env.docker up --build` levanta app + PostgreSQL,
  `GET /salud` responde `ok`, y la interfaz carga con los datos de `seed_demo`.
- Ajustar lo que falle (rutas, permisos, healthcheck). Ver `docs/arquitectura/despliegue.md`.

---

## B. Mejoras de la interfaz / UX (Módulo 1)

### B1 🟡👤 Entrada simplificada de movimientos
Hoy "Registrar movimiento" pide cuenta + débito + crédito por línea. Para el uso diario (y
para el chatbot de WhatsApp) hace falta un **"entró / salió plata"** que elija las cuentas
solo, según un **tipo de movimiento**.
- **Decisión 👤**: la lista de tipos de movimiento y a qué cuentas mapea cada uno. Ejemplos
  a validar: *venta de contado*, *compra de contado*, *pago de servicio*, *retiro del dueño*,
  *aporte del dueño*, *préstamo recibido*, *pago de préstamo*, *gasto de nómina*,
  *traslado caja↔bancos*.
- **Dónde**: `app/features/movimientos/` (un servicio nuevo `registrar_movimiento_simple`
  que arma las líneas), un endpoint `POST /movimientos/simple`, y una pantalla nueva o un
  modo de la actual en `app/web/`.
- **Listo cuando**: se puede registrar "entró $500.000 a bancos por una venta" en un
  formulario sin pensar en débito/crédito, y el asiento resultante es el correcto; con
  tests por cada tipo.
- Actualizar `docs/features/movimientos/spec.md`.

### B2 🟢 Editar el enlace a un documento desde la interfaz
Hoy el enlace (RUT / PDF) se pone al crear, o después con `PATCH` de la API. Falta un botón
"editar enlace" en las tablas de Terceros / Facturas / Contratos.
- **Dónde**: solo `app/web/` (el `PATCH` ya existe). Sin cambios de backend.
- **Listo cuando**: desde cada tabla se puede pegar/cambiar el enlace de una fila.

### B3 🟢 Números de factura / consecutivos
Hoy el `numero` de la factura lo escribe el usuario. Evaluar consecutivo automático para
las emitidas (las recibidas siempre traen su número del proveedor).
- **Decisión 👤**: ¿hace falta, o el usuario prefiere copiar el número de su talonario?

---

## C. Módulo 2 — WhatsApp (chatbot 100 % determinístico)

> **Recordatorio**: nada de IA en el Módulo 2. Ver `docs/aprendizaje/deterministico-vs-ia.md`.
> El plan completo del Módulo 2 está en el plan aprobado (`~/.claude/plans/`), Etapas 3–5.

### C1 👤 Decidir el proveedor de WhatsApp
Meta Cloud API directo vs. Twilio. Se construye contra una interfaz `ProveedorWhatsApp` con
un adaptador `Fake` para tests, así que la decisión no bloquea el desarrollo — pero sí hace
falta para conectar un número real.
- Escribir `docs/aprendizaje/whatsapp-cloud-api-vs-twilio.md` con la comparación.

### C2 Documentar el Módulo 2 (Etapa 3)
Escribir un `spec.md` por feature en `docs/features/whatsapp-*/`: proveedor, webhook,
conversaciones, asistente, y los flujos (factura, pago, contrato, movimiento, consulta
balance). Payloads de webhook de ejemplo, pasos de cada flujo, textos del menú y la ayuda,
tabla `conversacion`.
- **Se puede partir en varios chats**: uno para "infraestructura" (proveedor + webhook +
  conversaciones + asistente), uno por cada flujo.

### C3 Construir el Módulo 2 (Etapa 4)
Por feature, con su spec ya escrito: `app/features/whatsapp/`. Interfaz `ProveedorWhatsApp`
+ `FakeProvider`, webhook (`GET`/`POST /whatsapp/webhook`), motor de conversación,
asistente (menú/ayuda/cancelar/intención), y los 5 flujos. Cada flujo llama a los servicios
del Módulo 1 que ya existen.
- **Listo cuando**: un test de integración por flujo (POST de payload de webhook → estado
  en BD + mensaje capturado por el `FakeProvider`), y el script de simulación de consola.

### C4 Simulador de WhatsApp en la interfaz + script de consola (Etapa 5)
Pestaña "Simulador" en `app/web/` que postea a `/whatsapp/webhook` y muestra la
conversación, más `scripts/simular_conversacion.py`.

---

## D. Contabilidad — profundizar (probablemente Módulo 4)

### D1 🟢 Sub-cuentas (plan de cuentas jerárquico)
Para "Bancos → Banco A / Banco B" como cuentas separadas (hoy se resuelve filtrando por
`tercero_id`). Requiere `cuenta.cuenta_padre_id` y que el árbol de la interfaz sume un
nivel. Ver `docs/features/balance/spec.md §8`.

### D2 🟢 Ítems de factura / retenciones / pagos parciales
Necesarios para acercarse a facturación electrónica DIAN. Son cambios aditivos (nuevas
tablas), no reescrituras. Ver `docs/features/facturas/spec.md §8` y `pagos/spec.md §8`.

### D3 🟢 IVA en dos cuentas (generado / descontable)
Hoy el IVA está neteado en `2408`. Si hay que declarar IVA formal, se parte en dos. Ver
`docs/features/contabilidad-nucleo/spec.md §8`.

### D4 🟢 Reportes con corte por periodo real y estados financieros
Balance general y estado de resultados con estructura NIIF. Es el Módulo 4 del roadmap.

---

## E. Infraestructura / calidad

### E1 🟢 CI (GitHub Actions)
Correr `pytest` + `ruff` en cada push. Un solo archivo `.github/workflows/ci.yml`.

### E2 🟢 Backups de la base de datos
En producción lo da el PostgreSQL gestionado del proveedor de nube; documentar el
procedimiento.
