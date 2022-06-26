import asyncio
from collections import defaultdict
from typing import DefaultDict, Optional

from fastapi import HTTPException

from app.models.items.queries import (
    count_elements_with_ids,
    get_items,
    get_items_by_ids_and_type,
)
from app.schemas import ImportItem
from app.types import ItemType


class AsyncChecks:
    def __init__(self, items: list[ImportItem]):
        self.items = items
        self._request_item_ids: Optional[list[str]] = None
        self._request_parent_ids: Optional[list[str]] = None
        self._not_null_parent_ids_must_be_in_db: Optional[list[str]] = None
        self._item_type_by_id: Optional[DefaultDict[str, ItemType]] = None
        self.__prepare_data()

    def __prepare_data(self) -> None:
        self._request_item_ids = []
        self._request_parent_ids = []
        self._item_type_by_id = defaultdict(str)  # type:ignore

        for item in self.items:
            self._request_item_ids.append(str(item.id))
            self._item_type_by_id[str(item.id)] = item.type
            if (parent_id := item.parentId) is not None:
                self._request_parent_ids.append(str(parent_id))

        self._not_null_parent_ids_must_be_in_db = list(
            {
                parentId
                for parentId in self._request_parent_ids
                if parentId and parentId not in self._request_item_ids
            }
        )

    async def _check_all_parents_are_exist(self) -> None:
        assert self._not_null_parent_ids_must_be_in_db is not None

        parent_items_count = await count_elements_with_ids(
            self._not_null_parent_ids_must_be_in_db
        )

        if len(self._not_null_parent_ids_must_be_in_db) != parent_items_count:
            err = "Not all parents exist for items: neither in request nor in database"  # noqa
            raise HTTPException(status_code=400, detail=err)

    async def _check_all_parents_are_actually_parents(self) -> None:
        assert self._not_null_parent_ids_must_be_in_db is not None

        offer_parents = await get_items_by_ids_and_type(
            item_ids=self._not_null_parent_ids_must_be_in_db,
            item_type=ItemType.offer.value,
        )
        if offer_parents:
            detail = f"Some of parents are actually {ItemType.offer.value}, not {ItemType.category.value}"  # noqa
            raise HTTPException(status_code=400, detail=detail)

    async def _check_category_is_not_changed(self) -> None:
        assert self._request_item_ids is not None
        assert self._item_type_by_id is not None

        items_already_in_db = await get_items(item_ids=self._request_item_ids)
        errs = []
        for item in items_already_in_db:
            item_id = str(item.id)
            if item.type != self._item_type_by_id[item_id]:
                errs.append(item_id)

        if errs:
            ids = "\n".join(errs)
            detail = f"Import can't change type of item. Changed for this items:\n{ids}"
            raise HTTPException(status_code=400, detail=detail)

    async def check(self) -> None:
        await asyncio.gather(
            *[
                self._check_all_parents_are_exist(),
                self._check_all_parents_are_actually_parents(),
                self._check_category_is_not_changed(),
            ]
        )
