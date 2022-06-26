from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, TypedDict


class ItemType(str, Enum):
    offer = "OFFER"
    category = "CATEGORY"


class DbItemWithAddInfo(TypedDict):
    id: str
    date: str
    name: str
    type: str
    parent_id: Optional[str]
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


@dataclass
class DbItem:
    id: str
    name: str
    type: ItemType
    date: str
    price: Optional[int] = None
    parent_id: Optional[str] = None


class ImportItemToDb(TypedDict):
    id: str
    date: datetime
    name: str
    type: str
    parent_id: Optional[str]
    price: Optional[int]


class ImportStatsItemToDb(TypedDict):
    stat_id: str
    id: str
    name: str
    price: int
    parent_id: Optional[str]
    type: str
    date: datetime
