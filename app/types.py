from __future__ import annotations

from enum import Enum
from typing import Optional, TypedDict


class DbItemWithAddInfo(TypedDict):
    id: str
    date: str
    name: str
    type: str
    parentId: Optional[str]
    price: Optional[int]
    children: Optional[list[DbItemWithAddInfo]]  # type: ignore

    # additional info
    lvl: int
    total_price: int
    total_offer_count: int


class ItemsOut(TypedDict):
    id: str
    date: str
    name: str
    type: str
    parentId: Optional[str]
    price: Optional[int]
    children: Optional[list["ItemsOut"]]  # type: ignore


class ItemType(str, Enum):
    offer = "OFFER"
    category = "CATEGORY"
