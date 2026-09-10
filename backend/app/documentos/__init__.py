"""Enlaces a documentos de respaldo (RUT, PDF de factura/contrato).

En v1 es una URL de texto (típicamente un enlace de Drive). Toda la lógica
vive en `enlace.py` para que el día que se pase a almacenamiento real
(S3 o similar) el cambio esté acotado. Ver docs/features/documentos/spec.md.
"""
