import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from app.db.base import metadata

items_statistic_table = sa.Table(
    "items_statistic",
    metadata,
    sa.Column("stat_id", postgresql.UUID(), primary_key=True, index=True, nullable=False),
    sa.Column("id", postgresql.UUID(), index=True, nullable=False),
    sa.Column("name", sa.String(), nullable=False),
    sa.Column("price", sa.BigInteger(), nullable=False),
    sa.Column("parent_id", postgresql.UUID(), nullable=True, index=True),
    sa.Column("type", sa.String(length=8), nullable=False),
    sa.Column("date", postgresql.TIMESTAMP(timezone=True), nullable=False),
    sa.CheckConstraint("price >= 0", name="items_stat_price_check_gte_0"),
    sa.UniqueConstraint("id", "parent_id", "date", name="id_parent_id_date_uix"),
    sa.ForeignKeyConstraint(
        ["id"],
        ["items.id"],
        ondelete="CASCADE",
        name="items_stat_id_f0ab547a_fk_items_id",
    ),
)
