from fastapi import APIRouter, Query
from starlette.responses import RedirectResponse

from app.api.items.handlers import RecursiveSQLOnlyItems
from app.errors import NodeNotFound, InvalidUUID
from app.models.items.queries import check_if_item_exists, cascade_delete_item_by_id
from app.types import ItemsOut
from app.utils import is_valid_uuid

api_router = APIRouter()


@api_router.get("/", include_in_schema=False)
async def docs_redirect() -> RedirectResponse:
    return RedirectResponse(url="/docs")


@api_router.get(
    "/nodes",
    description="Получить информацию об элементе по идентификатору."
    " При получении информации о категории также предоставляется информация о её дочерних элементах.",  # noqa
)
async def get_nodes_with_children_by_id(
    id: str = Query(
        ...,
        example="3fa85f64-5717-4562-b3fc-2c963f66a333",
        description="Идентификатор элемента",
    ),
) -> ItemsOut:
    if not is_valid_uuid(id):
        raise InvalidUUID(uuid=id)

    recursive_nodes = RecursiveSQLOnlyItems(start_item_id=id)
    nodes = await recursive_nodes.get()
    if not nodes:
        raise NodeNotFound(node_id=id)

    return nodes


@api_router.get(
    "/delete",
    description="Удалить элемент по идентификатору."
    " При удалении категории удаляются все дочерние элементы."
    " Доступ к статистике (истории обновлений) удаленного элемента невозможен.",
)
async def delete_item_by_id(
    id: str = Query(
        ...,
        example="3fa85f64-5717-4562-b3fc-2c963f66a333",
        description="Идентификатор элемента",
    ),
) -> None:
    if not is_valid_uuid(id):
        raise InvalidUUID(uuid=id)

    if not await check_if_item_exists(id):
        raise NodeNotFound(node_id=id)

    await cascade_delete_item_by_id(id)
