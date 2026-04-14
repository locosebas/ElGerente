# Modelo de Negocio — El Gerente

**Fecha**: 2026-04-10

## Propuesta de valor por actor

### Para el dueño del negocio
- **Gratis**: almacenamiento, registro de transacciones, inventario básico, para-contabilidad
- **Pago**: análisis de ineficiencias, reportes avanzados, predicciones, recomendaciones

### Para el operador de la plataforma (nosotros)
- **Datos** de todos los negocios → análisis micro y macroeconómicos
- **Predicciones** si se alcanza masa crítica de clientes
- **Monetización adicional**: ofrecer productos que mejoren la calidad de los negocios
  (Ejemplos posibles: crédito, seguros, proveedores, software especializado)

## Modelo freemium

| Tier | Qué incluye | Precio |
|---|---|---|
| Free | Almacenamiento, transacciones básicas, inventario, para-contabilidad | $0 |
| Pro | Análisis de ineficiencias, reportes, alertas, predicciones | Pago |
| (Futuro) | Productos derivados (crédito, proveedores, etc.) | Comisión / suscripción |

## Estrategia de datos

- Los datos pertenecen a la plataforma (definir en ToS)
- Agregación cross-negocio para análisis macro
- Con suficiente volumen → modelos predictivos sectoriales
- Datos anonimizados para análisis macro; datos por negocio para análisis micro (cliente Pro)

## Implicaciones arquitectónicas clave

- **Multi-tenant desde día 1** — cada negocio es un tenant aislado
- **Capa de analytics separada** — tenant data ≠ analytics data
- **Pipeline de datos** — ingesta → normalización → agregación
- **Privacidad/legal** — ToS debe cubrir propiedad y uso de datos

## Riesgos identificados

- Regulación de datos (GDPR-equivalente en mercado objetivo)
- Confianza del usuario si percibe que sus datos se venden
- Masa crítica necesaria para que los análisis macro sean valiosos
