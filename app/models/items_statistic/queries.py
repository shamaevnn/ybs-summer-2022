import json
import uuid
from datetime import datetime, timedelta

from sqlalchemy.dialects.postgresql import insert

from app.db.base import database
from app.models.items_statistic.table_schema import items_statistic_table
from app.schemas import ImportItem, StatsItem, StatsItems
from app.types import ImportStatsItemToDb


async def get_offer_stats_for_n_hours_and_date(
    date: datetime, n_hours: int = 24
) -> StatsItems:
    """
    stats for [date - n_hours, date]
    """
    date_fmt = "%Y-%m-%d %H:%M:%S"

    date_n_hours_ago = date - timedelta(hours=n_hours)
    date_left = date_n_hours_ago.strftime(date_fmt)
    date_right = date.strftime(date_fmt)

    query = """
    SELECT
        json_build_object(
            'items',
            array_agg(json_build_object(
                'id', items.id,
                'name', items.name,
                'price', items.price,
                'parentId', items.parent_id,
                'type', items.type,
                'date', items.date
            ))
        ) as res
    FROM items_statistic stats
    LEFT JOIN items on stats.id = items.id
    WHERE stats.date >= '%s' AND stats.date <= '%s'
    """ % (
        date_left,
        date_right,
    )
    fetched_data = await database.fetch_all(query)
    if not fetched_data:
        return StatsItems(items=[])

    _res = json.loads(fetched_data[0]["res"])
    res: StatsItems = StatsItems.parse_obj(_res)
    return res


async def save_import_item_to_statistic(item: ImportItem, date: datetime) -> None:
    stmt = insert(items_statistic_table)
    query = stmt.on_conflict_do_nothing(index_elements=["id", "parent_id", "date"])

    values = dict(date=date, parent_id=item.parentId, **item.dict())
    values.pop("parentId")
    values["stat_id"] = uuid.uuid4()

    await database.execute(query, values=values)


async def save_import_items_to_statistic(items: list[ImportStatsItemToDb]) -> None:
    stmt = insert(items_statistic_table)
    query = stmt.on_conflict_do_nothing(index_elements=["id", "parent_id", "date"])

    await database.execute_many(query=query, values=items)
