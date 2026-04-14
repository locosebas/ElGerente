# Mercado Objetivo — El Gerente

**Fecha**: 2026-04-10

## Mercado inicial: Colombia

### Contexto fiscal relevante
- **Facturación electrónica**: obligatoria ante la DIAN (Dirección de Impuestos y Aduanas Nacionales)
- **Formato**: UBL 2.1 (estándar DIAN)
- **Identificación**: Cédula (personas naturales) / NIT (empresas)
- **Impuesto principal**: IVA (19% general, con tarifas diferenciales)
- **Régimen simplificado**: muchos negocios pequeños pueden estar en régimen simple — no obligados a facturar electrónicamente ante DIAN en todos los casos

### Implicación para el MVP
- Decisión pendiente: ¿factura electrónica DIAN-compliant desde día 1, o factura interna (no fiscal) primero?
- Lectura de cédula/NIT para pre-llenar datos del cliente → agiliza la caja
- Moneda: COP (pesos colombianos)

## Expansión futura
- Otros mercados LATAM (Chile, México, etc.) — arquitectura debe ser multi-país desde el diseño
