"""Serialización de asientos a la forma que espera `AsientoOut`.

Vive aparte del router porque lo usan dos routers (contabilidad y
movimientos) y un router no debe importar de otro.
"""
from __future__ import annotations

from app.contabilidad.models import Asiento


def serializar_asiento(asiento: Asiento) -> dict:
    """AsientoOut necesita cuenta_codigo/cuenta_nombre por línea, que viven
    en la cuenta relacionada — por eso no se devuelve el objeto ORM tal cual.
    """
    return {
        "id": asiento.id,
        "fecha": asiento.fecha,
        "descripcion": asiento.descripcion,
        "origen": asiento.origen,
        "libro": asiento.libro,
        "documento_soporte": asiento.documento_soporte,
        "tercero_id": asiento.tercero_id,
        "tercero_nombre": asiento.tercero.nombre if asiento.tercero else None,
        "created_at": asiento.created_at,
        "lineas": [
            {
                "cuenta_codigo": linea.cuenta.codigo,
                "cuenta_nombre": linea.cuenta.nombre,
                "debito": linea.debito,
                "credito": linea.credito,
            }
            for linea in asiento.lineas
        ],
    }
