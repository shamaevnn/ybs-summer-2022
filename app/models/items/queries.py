import json
from typing import Optional, Tuple

from app.db.base import database
from app.types import DbItemWithAddInfo


async def get_items_tree_with_additional_info(
    start_node_uuid: str,
) -> Optional[DbItemWithAddInfo]:
    """
    check example of response in app/examples/db_item_with_add_info.json
    """
    query = (
        """
        WITH RECURSIVE c AS (
            SELECT *, parent_id as parentId, 0 as lvl
            FROM   items
            WHERE  items.id = '%s'
                UNION ALL
            SELECT items.*, items.parent_id as parentId, c.lvl + 1
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
