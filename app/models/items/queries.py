import json
from datetime import datetime
from typing import Iterable, Optional

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql.functions import count

from app.db.base import database
from app.models.items.table_schema import items_table
from app.types import DbItem, DbItemWithAddInfo, ImportItemToDb


async def get_items_tree_with_additional_info(
    start_node_uuid: str,
) -> Optional[DbItemWithAddInfo]:
    """
    check example of response in app/examples/db_item_with_add_info.json
    """
    query = (
        """
        WITH RECURSIVE c AS (
            SELECT *, 0 as lvl
            FROM   items
            WHERE  items.id = '%s'
                UNION ALL
            SELECT items.*, c.lvl + 1
            FROM   items
            JOIN   c ON items.parent_id = c.id
        ),
        maxlvl AS (SELECT max(lvl) maxlvl FROM c),
        j AS (
                SELECT
                    c.*, 0 as total_price, 0 as total_offer_count,
                    CASE
                        WHEN c.type = 'OFFER' THEN null
                    ELSE
                        json '[]'
                    END AS children
                FROM   c, maxlvl
                WHERE  lvl = maxlvl
            UNION ALL
                -- c - current parent
                -- j - child of parent
                SELECT
                    (c).*,
                    CASE
                        WHEN (
                            select s[1] from array_agg((j).type) -- first child
                        s) = 'OFFER' THEN
                            (SELECT SUM(s) FROM UNNEST(array_agg((j).price)) s)::integer
                        ELSE
                            (
                                SELECT SUM(s) FROM UNNEST(array_agg((j).total_price)) s
                            )::integer
                    END as total_price,

                    CASE
                        WHEN (
                            select s[1] from array_agg((j).type) -- first child
                        s) = 'OFFER' THEN
                            (SELECT array_length(array_agg((j).price), 1))::integer
                        ELSE
                            (
                                SELECT SUM(s) FROM UNNEST(array_agg((j).total_offer_count)
                            ) s)::integer
                    END as total_offer_count,

                    array_to_json(
                        array_agg(j) || array(
                            SELECT r FROM (
                                SELECT
                                    l.*, json '[]' children
                                FROM  c l, maxlvl
                                WHERE
                                    l.parent_id = (c).id
                                AND
                                    l.lvl < maxlvl
                                AND
                                NOT EXISTS (
                                    SELECT 1 FROM   c lp WHERE  lp.parent_id = l.id
                                )
                            ) r
                        )
                    ) children
                FROM (
                    SELECT c, j
                    FROM   c
                    JOIN   j ON j.parent_id = c.id
                ) v
                GROUP BY v.c
        )
        SELECT jsonb_pretty(row_to_json(j)::jsonb) as json_tree
        FROM   maxlvl, j
        WHERE  lvl = 0;
    """
        % start_node_uuid
    )
    fetched_data = await database.fetch_all(query)
    if not fetched_data or not (_tree := json.loads(fetched_data[0].json_tree)):
        return None
    tree: DbItemWithAddInfo = _tree
    return tree


async def get_all_children_ids_by_item_id(item_id: str) -> list[str]:
    """
    example or query response:
    {
        "children_ids" : [
            "863e1a7a-1304-42ae-943b-179184c077e3",
            "b1d8fd7d-2ae3-47d5-b2f9-0f094af800d4"
        ]
    }
    function returns [
        "863e1a7a-1304-42ae-943b-179184c077e3",
        "b1d8fd7d-2ae3-47d5-b2f9-0f094af800d4"
    ]
    or [] if there are no children
    """
    query = (
        """
        WITH RECURSIVE cte AS (
            SELECT id AS root_id, id, parent_id
            FROM items
            WHERE items.id = '%s'
                UNION ALL
            SELECT cte.root_id, items.id, items.parent_id
            FROM items
            JOIN cte ON items.parent_id = cte.id
        )
        SELECT
            json_build_object(
                'chidlren_ids', array_agg(id)
            ) as res
        FROM cte
        WHERE id <> root_id
        GROUP BY root_id
    """
        % item_id
    )
    fetched_data = await database.fetch_all(query)
    if not fetched_data or not (_res := json.loads(fetched_data[0].res)):
        return []
    res: list[str] = _res["children_ids"]
    return res


async def get_all_parent_ids_by_item_id(item_id: str) -> list[str]:
    query = (
        """
    WITH RECURSIVE cte AS (
        SELECT id AS root_id, id, parent_id
        FROM items
        WHERE items.id = '%s'
            UNION ALL
        SELECT cte.root_id, items.id, items.parent_id
        FROM items
        JOIN cte ON items.id = cte.parent_id
    )
    SELECT
        json_build_object(
            'parent_ids', array_agg(id)
        ) as res
    FROM cte
    WHERE id <> root_id
    GROUP BY root_id;
    """
        % item_id
    )

    fetched_data = await database.fetch_all(query)
    if not fetched_data or not (_res := json.loads(fetched_data[0].res)):
        return []
    res: list[str] = _res["parent_ids"]
    return res


async def update_date(item_ids: list[str], new_update_date: datetime) -> None:
    query = (
        items_table.update()
        .where(items_table.c.id.in_(tuple(item_ids)))
        .values(
            {
                "date": new_update_date,
            }
        )
    )
    await database.execute(query)


async def cascade_delete_item_by_id(item_id: str) -> None:
    query = items_table.delete().where(items_table.c.id == item_id)
    await database.execute(query)


async def check_if_item_exists(item_id: str) -> bool:
    query = sa.select([items_table.c.id]).where(items_table.c.id == item_id)
    res = await database.fetch_one(query)
    return bool(res)


async def get_items(item_ids: list[str]) -> list[DbItem]:
    query = sa.select(*[items_table.c]).where(items_table.c.id.in_(tuple(item_ids)))
    fetched_data = await database.fetch_all(query)
    if not fetched_data:
        return []
    return [DbItem(**item) for item in fetched_data]


async def count_elements_with_ids(item_ids: list[str]) -> int:
    query = sa.select([count(items_table.c.id)]).where(
        items_table.c.id.in_(tuple(item_ids))
    )
    fetched_data = await database.fetch_one(query)
    if not fetched_data:
        return 0
    res: int = fetched_data[0]
    return res


async def get_items_by_ids_and_type(item_ids: list[str], item_type: str) -> list[DbItem]:
    query = sa.select(*[items_table.c]).where(
        sa.and_(
            *[
                items_table.c.id.in_(tuple(item_ids)),
                items_table.c.type == item_type,
            ]
        )
    )
    fetched_data = await database.fetch_all(query)
    if not fetched_data:
        return []
    return [DbItem(**item) for item in fetched_data]


async def filter_ids_in_db(item_ids: Iterable[str]) -> list[str]:
    query = sa.select([items_table.c.id]).where(items_table.c.id.in_(tuple(item_ids)))
    fetched_data = await database.fetch_all(query)
    if not fetched_data:
        return []
    return [str(row.id) for row in fetched_data]


async def upsert_items(items: list[ImportItemToDb]) -> None:
    stmt = insert(items_table)
    query = stmt.on_conflict_do_update(
        constraint="items_pkey",
        # The columns that should be updated on conflict
        set_={
            # dont include type
            "name": stmt.excluded.name,
            "price": stmt.excluded.price,
            "parent_id": stmt.excluded.parent_id,
            "date": stmt.excluded.date,
        },
    )
    await database.execute_many(query=query, values=items)
