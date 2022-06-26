from dataclasses import asdict
from datetime import datetime
from typing import cast
from uuid import UUID

from fastapi import APIRouter, Body, HTTPException, Query
from starlette.responses import RedirectResponse

from app.api import descriptions
from app.api.items.handlers import ImportItemsManager, RecursiveSQLOnlyItems
from app.errors import InvalidUUID, NodeNotFound
from app.models.items.queries import cascade_delete_item_by_id, check_if_item_exists
from app.models.items_statistic.queries import get_offer_stats_for_n_hours_and_date
from app.schemas import (
    DictExampleImportItem,
    ImportItem,
    ImportItemsIn,
    StatsItems,
    SaleStatsDateIn,
)
from app.types import ItemsOut
from app.utils import is_valid_uuid

api_router = APIRouter(tags=["Default items endpoints"])
statistic_api_router = APIRouter(tags=["Additional endpoints with statistics"])


@api_router.get("/", include_in_schema=False)
async def docs_redirect() -> RedirectResponse:
    return RedirectResponse(url="/docs")


@api_router.get(
    "/nodes/{id}",
    description=descriptions.get_nodes,
)
async def get_nodes_with_children_by_id(
    id: UUID = Query(
        ...,
        example="3fa85f64-5717-4562-b3fc-2c963f66a333",
        description="Идентификатор элемента",
    ),
) -> ItemsOut:
    str_id = str(id)
    if not is_valid_uuid(str_id):
        raise InvalidUUID(uuid=str_id)

    recursive_nodes = RecursiveSQLOnlyItems(start_item_id=str_id)
    nodes = await recursive_nodes.get()

    return nodes


@api_router.delete(
    "/delete/{id}",
    description=descriptions.delete_node,
)
async def delete_item_by_id(
    id: UUID = Query(
        ...,
        example="74b81fda-9cdc-4b63-8927-c978afed5cf4",
        description="Идентификатор элемента",
    ),
) -> None:
    str_id = str(id)

    if not is_valid_uuid(str_id):
        raise InvalidUUID(uuid=str_id)

    if not await check_if_item_exists(str_id):
        raise NodeNotFound(node_id=str_id)

    await cascade_delete_item_by_id(str_id)


@api_router.post(
    "/imports",
    description=descriptions.imports,
)
async def import_items(
    updateDate: datetime = Body(...),
    items: list[DictExampleImportItem] = Body(...),
) -> None:
    try:
        validated = ImportItemsIn(
            items=[ImportItem(**asdict(item)) for item in items],
            updateDate=updateDate,
        )
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    else:
        items_to_import = ImportItemsManager(
            items_to_import=validated.items,
            update_date=validated.updateDate,
        )
        await items_to_import.import_to_db()


@statistic_api_router.get(
    "/sales", description=descriptions.sales, response_model=StatsItems
)
async def get_sales(
    date: str = Query(
        ...,
        example="2022-02-03T12:00:00.000Z",
        description="Дата и время запроса.",
    ),
) -> StatsItems:

    try:
        validated = SaleStatsDateIn(date=date)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid date format {date}")
    else:
        validated_date: datetime = cast(datetime, validated.date)

    res = await get_offer_stats_for_n_hours_and_date(date=validated_date)
    return res
