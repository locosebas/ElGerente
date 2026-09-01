"""Configuración de la base de datos.

SQLite para empezar (un archivo, sin servidor que instalar). Cambiar a
PostgreSQL más adelante es solo cambiar DATABASE_URL — el resto del
código (modelos, queries via el ORM) no se toca.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = "sqlite:///./elgerente.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass
