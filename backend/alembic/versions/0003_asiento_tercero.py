"""asiento.tercero_id — con qué actor externo se hizo la transacción

Revision ID: 0003_asiento_tercero
Revises: 0002_enlaces_documentos
Create Date: 2026-09-09

Ver docs/features/terceros/spec.md y docs/features/contabilidad-nucleo/spec.md.
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0003_asiento_tercero"
down_revision: str | None = "0002_enlaces_documentos"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("asiento", schema=None) as batch_op:
        batch_op.add_column(sa.Column("tercero_id", sa.Integer(), nullable=True))
        batch_op.create_index(
            batch_op.f("ix_asiento_tercero_id"), ["tercero_id"], unique=False
        )
        batch_op.create_foreign_key(
            "fk_asiento_tercero", "tercero", ["tercero_id"], ["id"]
        )


def downgrade() -> None:
    with op.batch_alter_table("asiento", schema=None) as batch_op:
        batch_op.drop_constraint("fk_asiento_tercero", type_="foreignkey")
        batch_op.drop_index(batch_op.f("ix_asiento_tercero_id"))
        batch_op.drop_column("tercero_id")
