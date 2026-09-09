"""Configuración leída del entorno (archivo .env o variables reales).

Un solo lugar centraliza todos los ajustes. El resto del código pide
`get_settings()` y nunca lee variables de entorno por su cuenta.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Base de datos: el único punto que cambia para pasar de SQLite a PostgreSQL.
    database_url: str = "sqlite+aiosqlite:///./elgerente.db"

    # WhatsApp (Módulo 2).
    whatsapp_proveedor: Literal["fake", "meta"] = "fake"
    whatsapp_verify_token: str = "cambia-esto"
    meta_access_token: str = ""
    meta_phone_number_id: str = ""

    entorno: Literal["dev", "prod"] = "dev"

    @property
    def es_dev(self) -> bool:
        return self.entorno == "dev"


@lru_cache
def get_settings() -> Settings:
    """Se cachea: la configuración se lee una sola vez por proceso.

    En los tests se limpia con `get_settings.cache_clear()` si hace falta
    forzar otra configuración.
    """
    return Settings()
