"""Integración — interfaz gráfica HTML. Ver docs/features/web-ui/spec.md §7.

No se prueba el comportamiento del navegador (esa lógica es la de la API,
ya cubierta): solo que las páginas y los estáticos se sirven, y que montar
el StaticFiles en `/` no rompe la API.
"""
from __future__ import annotations


async def test_home_sirve_html(client):
    r = await client.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
    assert "/static/app.js" in r.text
    assert "/static/styles.css" in r.text


async def test_estaticos_se_sirven(client):
    for ruta, tipo in [("/static/app.js", "javascript"), ("/static/styles.css", "css")]:
        r = await client.get(ruta)
        assert r.status_code == 200, ruta
        assert tipo in r.headers["content-type"]


async def test_api_sigue_respondiendo_con_ui_montada(client):
    r = await client.get("/cuentas")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
