from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Union
from uuid import UUID

from pydantic import BaseModel, root_validator, validator

from app.types import ItemType


@dataclass
class DictExampleImportItem:
    id: UUID
    name: str
    type: ItemType
    parentId: Optional[UUID] = None
    price: Optional[int] = None


class ImportItem(BaseModel):
    id: UUID
    name: str
    type: ItemType
    parentId: Optional[UUID] = None
    price: Optional[int] = None

    @classmethod
    def _validate_price_for_cats(cls, type: ItemType, price: Optional[int]) -> None:
        if type == ItemType.category.value:
            if price is not None:
                raise ValueError(
                    f"{ItemType.category.value=} must not have price. Now {price=}"
                )
        elif type == ItemType.offer.value:
            if price is None:
                raise ValueError(
                    f"{ItemType.offer.value=} must have price, now it's None"
                )
            if price < 0:
                raise ValueError("Offer must have price >= 0")

    @classmethod
    def _validate_id_ne_parent_id(cls, id: UUID, parent_id: Optional[UUID]) -> None:
        if parent_id and id == parent_id:
            raise ValueError(f"id can't be equal to parentId: {id}, {parent_id}")

    @root_validator
    def validate_item(
        cls, values: dict[str, Union[UUID, str, ItemType, int, None]]
    ) -> dict[str, Union[UUID, str, ItemType, int, None]]:
        cls._validate_price_for_cats(
            type=values["type"], price=values.get("price")  # type: ignore
        )
        cls._validate_id_ne_parent_id(
            id=values["id"], parent_id=values.get("parentId")  # type: ignore
        )
        return values


class ImportItemsIn(BaseModel):
    items: list[ImportItem]
    updateDate: datetime

    @classmethod
    def _validate_all_item_ids_are_unique(cls, item_ids: list[UUID]) -> None:
        if len(item_ids) != len(set(item_ids)):
            raise ValueError("All ids must be unique")

    @validator("items")
    def validate_items(cls, items: list[ImportItem]) -> list[ImportItem]:
        item_ids = [item.id for item in items]
        cls._validate_all_item_ids_are_unique(item_ids)
        return items
