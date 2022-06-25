import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from app.db.base import metadata

items_table = sa.Table(
    "items",
    metadata,
    sa.Column("id", postgresql.UUID(), primary_key=True, index=True, nullable=False),
    sa.Column("name", sa.String(), nullable=False),
    sa.Column("price", sa.BigInteger(), nullable=True),
    sa.Column("parent_id", postgresql.UUID(), nullable=True, index=True),
    sa.Column("type", sa.String(length=8), nullable=False),
    sa.Column("date", postgresql.TIMESTAMP(timezone=True), nullable=False),
    sa.CheckConstraint("price >= 0 or price is null", name="items_price_check_gte_0"),
    sa.UniqueConstraint("id", "parent_id", name="id_parent_id_uix"),
    sa.ForeignKeyConstraint(
        ["parent_id"],
        ["items.id"],
        ondelete="CASCADE",
        name="items_parent_id_f0ab547a_fk_items_id",
        # initially="DEFERRED",
        # deferrable=True,
    ),
)
