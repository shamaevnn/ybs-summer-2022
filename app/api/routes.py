import time

from fastapi import APIRouter, Query
from starlette.responses import RedirectResponse

from app.api.nodes.handlers import RecursiveSQLOnlyItems
from app.errors import NodeNotFound
from app.types import ItemsOut

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
    recursive_nodes = RecursiveSQLOnlyItems(start_item_id=id)
    nodes = await recursive_nodes.get()
    if not nodes:
        raise NodeNotFound(node_id=id)

    return nodes
