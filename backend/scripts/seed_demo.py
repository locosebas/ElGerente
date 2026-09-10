"""Puebla la base de datos con datos inventados para ver el producto con
contenido (probar la interfaz, mostrarlo, etc.).

NO es para producción. Usa los servicios reales, así que la contabilidad
que genera es correcta (asientos que cuadran, etc.).

Requisitos: la base ya migrada y con el plan de cuentas sembrado
(`alembic upgrade head` + `python -m app.seed`).

    python scripts/seed_demo.py            # agrega los datos demo
    python scripts/seed_demo.py --forzar   # los agrega aunque ya haya facturas

Para empezar de cero:  python scripts/reset_db.py  &&  python scripts/seed_demo.py
"""
from __future__ import annotations

import asyncio
import sys
from datetime import date
from decimal import Decimal

from sqlalchemy import func, select

from app.contabilidad.models import LibroContable
from app.core.db import SessionLocal
from app.features.contratos.service import registrar_contrato
from app.features.facturas.models import Factura, TipoFactura
from app.features.facturas.service import registrar_factura
from app.features.movimientos.service import registrar_movimiento_manual
from app.features.pagos.service import pagar_factura
from app.features.terceros.models import TipoTercero
from app.features.terceros.service import crear_tercero

D = Decimal


async def _ya_hay_datos(session) -> bool:
    n = (await session.execute(select(func.count()).select_from(Factura))).scalar_one()
    return n > 0


async def poblar() -> None:  # noqa: PLR0915 — es un guion lineal, se lee de arriba a abajo
    async with SessionLocal() as s:
        if await _ya_hay_datos(s) and "--forzar" not in sys.argv:
            print(
                "Ya hay facturas en la base. Usá  python scripts/seed_demo.py --forzar  "
                "para agregar los datos demo igual, o  python scripts/reset_db.py  para "
                "empezar de cero."
            )
            return

        DRIVE = "https://drive.google.com/file/d/DEMO"

        print("Creando terceros...")
        prov_arriendo = await crear_tercero(
            s, nombre="Inmobiliaria El Roble", nit_cedula="830111222", tipo=TipoTercero.PROVEEDOR,
            enlace_rut=f"{DRIVE}-rut-elroble/view",
        )
        prov_mayorista = await crear_tercero(
            s, nombre="Distribuciones del Valle SAS", nit_cedula="900456789", tipo=TipoTercero.PROVEEDOR,
            enlace_rut=f"{DRIVE}-rut-delvalle/view",
        )
        prov_servicios = await crear_tercero(
            s, nombre="Energía y Aseo S.A.", nit_cedula="890333444", tipo=TipoTercero.PROVEEDOR
        )
        prov_papeleria = await crear_tercero(
            s, nombre="Papelería La Esquina", nit_cedula="43555666", tipo=TipoTercero.PROVEEDOR
        )
        cli_tienda = await crear_tercero(
            s, nombre="Tienda Doña Marta", nit_cedula="52123456", tipo=TipoTercero.CLIENTE
        )
        cli_restaurante = await crear_tercero(
            s, nombre="Restaurante La Fogata", nit_cedula="900789123", tipo=TipoTercero.CLIENTE
        )
        cli_hotel = await crear_tercero(
            s, nombre="Hotel Mirador", nit_cedula="811222333", tipo=TipoTercero.CLIENTE
        )

        print("Aporte inicial del dueño (movimiento oficial)...")
        await registrar_movimiento_manual(
            s,
            fecha=date(2026, 6, 1),
            descripcion="Aporte de capital del dueño para arrancar",
            libro=LibroContable.OFICIAL,
            documento_soporte="Consignación #001",
            lineas=[
                {"cuenta_codigo": "1110", "debito": "20000000", "credito": "0"},
                {"cuenta_codigo": "3115", "debito": "0", "credito": "20000000"},
            ],
        )

        print("Facturas recibidas (compras)...")
        # (numero, tercero, fecha, subtotal, iva, ¿pagada?, medio)
        compras = [
            ("ARR-2606", prov_arriendo, date(2026, 6, 3), "2500000", "0", True, "bancos"),
            ("DV-4471", prov_mayorista, date(2026, 6, 8), "6800000", "1292000", True, "bancos"),
            ("EA-9910", prov_servicios, date(2026, 6, 20), "480000", "91200", True, "caja"),
            ("ARR-2607", prov_arriendo, date(2026, 7, 3), "2500000", "0", True, "bancos"),
            ("DV-4620", prov_mayorista, date(2026, 7, 12), "7350000", "1396500", False, None),
            ("PLE-115", prov_papeleria, date(2026, 7, 15), "220000", "41800", True, "caja"),
            ("ARR-2608", prov_arriendo, date(2026, 8, 3), "2500000", "0", False, None),
            ("EA-10233", prov_servicios, date(2026, 8, 19), "510000", "96900", False, None),
        ]
        for i, (numero, tercero, fecha, subtotal, iva, pagada, medio) in enumerate(compras):
            f = await registrar_factura(
                s,
                tipo=TipoFactura.RECIBIDA,
                numero=numero,
                fecha=fecha,
                tercero_id=tercero.id,
                subtotal=D(subtotal),
                iva=D(iva),
                enlace_documento=f"{DRIVE}-{numero}/view" if i % 2 == 0 else None,
            )
            if pagada:
                await pagar_factura(s, factura_id=f.id, medio_pago=medio, fecha=fecha)

        print("Facturas emitidas (ventas)...")
        ventas = [
            ("FE-1001", cli_tienda, date(2026, 6, 10), "3200000", "608000", True, "bancos"),
            ("FE-1002", cli_restaurante, date(2026, 6, 25), "1850000", "351500", True, "bancos"),
            ("FE-1003", cli_hotel, date(2026, 7, 5), "9400000", "1786000", True, "bancos"),
            ("FE-1004", cli_tienda, date(2026, 7, 22), "2750000", "522500", False, None),
            ("FE-1005", cli_restaurante, date(2026, 8, 8), "2100000", "399000", True, "caja"),
            ("FE-1006", cli_hotel, date(2026, 8, 21), "6600000", "1254000", False, None),
        ]
        for numero, tercero, fecha, subtotal, iva, cobrada, medio in ventas:
            f = await registrar_factura(
                s,
                tipo=TipoFactura.EMITIDA,
                numero=numero,
                fecha=fecha,
                tercero_id=tercero.id,
                subtotal=D(subtotal),
                iva=D(iva),
            )
            if cobrada:
                await pagar_factura(s, factura_id=f.id, medio_pago=medio, fecha=fecha)

        print("Movimientos internos (para-contabilidad)...")
        internos = [
            (date(2026, 6, 30), "El dueño retira efectivo para gastos personales", "2905", "1105", "800000"),
            (date(2026, 7, 18), "Compra de mercancía sin factura a un vendedor ambulante", "5905", "1105", "350000"),
            (date(2026, 7, 31), "Retiro del dueño", "2905", "1110", "1500000"),
            (date(2026, 8, 15), "Propina/ayuda a un empleado, sin soporte", "5905", "1105", "120000"),
        ]
        for fecha, desc, cta_debito, cta_credito, monto in internos:
            await registrar_movimiento_manual(
                s,
                fecha=fecha,
                descripcion=desc,
                libro=LibroContable.INTERNA,
                documento_soporte=None,
                lineas=[
                    {"cuenta_codigo": cta_debito, "debito": monto, "credito": "0"},
                    {"cuenta_codigo": cta_credito, "debito": "0", "credito": monto},
                ],
            )

        print("Movimientos oficiales sueltos...")
        await registrar_movimiento_manual(
            s,
            fecha=date(2026, 7, 1),
            descripcion="Traslado de efectivo de caja a bancos",
            libro=LibroContable.OFICIAL,
            documento_soporte="Consignación #044",
            lineas=[
                {"cuenta_codigo": "1110", "debito": "1000000", "credito": "0"},
                {"cuenta_codigo": "1105", "debito": "0", "credito": "1000000"},
            ],
        )

        print("Contratos...")
        await registrar_contrato(
            s,
            tercero_id=prov_arriendo.id,
            objeto="Arrendamiento del local comercial (canon mensual $2.500.000)",
            valor=D("30000000"),
            fecha_inicio=date(2026, 6, 1),
            fecha_fin=date(2027, 5, 31),
            enlace_documento=f"{DRIVE}-contrato-arriendo/view",
        )
        await registrar_contrato(
            s,
            tercero_id=cli_hotel.id,
            objeto="Suministro mensual de insumos al Hotel Mirador",
            valor=D("72000000"),
            fecha_inicio=date(2026, 7, 1),
            fecha_fin=None,
        )

    print("\nListo. Datos demo cargados. Levantá el servidor y abrí http://localhost:8000/")


if __name__ == "__main__":
    asyncio.run(poblar())
