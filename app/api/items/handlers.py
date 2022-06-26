import uuid
from datetime import datetime
from typing import Optional, cast, Tuple

from app.api.items.checks import AsyncChecks
from app.db.base import database
from app.errors import NodeNotFound
from app.models.items.queries import (
    filter_ids_in_db,
    get_items_tree_with_additional_info,
    upsert_items,
    check_if_item_exists,
    get_all_parent_ids_by_item_id,
    update_date,
)
from app.models.items_statistic.queries import save_import_items_to_statistic
from app.schemas import ImportItem
from app.types import (
    DbItemWithAddInfo,
    ImportItemToDb,
    ItemsOut,
    ItemType,
    ImportStatsItemToDb,
)


class RecursiveSQLOnlyItems:
    def __init__(self, start_item_id: str):
        self.start_item_id = start_item_id

    @classmethod
    def __del_if_exists(cls, dictionary: DbItemWithAddInfo, key: str) -> None:
        if key in dictionary:
            del dictionary[key]  # type: ignore

    @classmethod
    def __delete_keys_values(
        cls, dictionary: DbItemWithAddInfo, keys: Optional[list[str]] = None
    ) -> None:
        if not keys:
            keys = ["total_price", "total_offer_count", "lvl", "parent_id"]

        for key in keys:
            cls.__del_if_exists(dictionary, key)

    @classmethod
    def _set_price_and_del_ambiguous_values(
        cls, curr_tree: DbItemWithAddInfo
    ) -> ItemsOut:
        curr_tree["parentId"] = curr_tree["parent_id"]
        curr_tree["date"] = curr_tree["date"].replace("+00:00", ".000Z")
        if curr_tree["type"] == ItemType.offer.value:
            # offer already has price
            cls.__delete_keys_values(curr_tree)
            return cast(ItemsOut, curr_tree)

        # categories
        children = curr_tree["children"]
        if not children:
            cls.__delete_keys_values(curr_tree)
            curr_tree["price"] = None
            return cast(ItemsOut, curr_tree)

        curr_tree["price"] = int(
            curr_tree["total_price"] / curr_tree["total_offer_count"]
        )
        cls.__delete_keys_values(curr_tree)

        new_children = []
        for child in children:
            child = cls._set_price_and_del_ambiguous_values(child)
            new_children.append(child)

        curr_tree["children"] = new_children
        return cast(ItemsOut, curr_tree)

    async def get(self) -> ItemsOut:
        if not (await check_if_item_exists(self.start_item_id)):
            raise NodeNotFound(node_id=self.start_item_id)

        _db_tree: Optional[DbItemWithAddInfo] = await get_items_tree_with_additional_info(
            self.start_item_id
        )
        assert _db_tree is not None
        db_tree: ItemsOut = self._set_price_and_del_ambiguous_values(_db_tree)
        return db_tree


class ImportItemsManager:
    def __init__(self, items_to_import: list[ImportItem], update_date: datetime):
        self.items_to_import = items_to_import
        self.update_date = update_date
        self._all_import_items_by_id: Optional[dict[str, ImportItem]] = None
        self._ids_already_in_db: Optional[list[str]] = None

    async def __prepare_data(self) -> None:
        self._all_import_items_by_id = {}
        all_ids = set()
        for item in self.items_to_import:
            self._all_import_items_by_id[str(item.id)] = item
            if item.parentId:
                _all_ids = {str(item.id), str(item.parentId)}
            else:
                _all_ids = {str(item.id)}
            all_ids.update(_all_ids)
        self._ids_already_in_db = await filter_ids_in_db(all_ids)

    def _get_item_to_upload(self, item: ImportItem) -> ImportItemToDb:
        item_dict = item.dict()
        res: ImportItemToDb = ImportItemToDb(  # type:ignore
            date=self.update_date, parent_id=item_dict.pop("parentId"), **item_dict
        )
        return res

    def _get_stat_item_to_upload(self, item: ImportItem) -> ImportStatsItemToDb:
        item_dict = item.dict()
        res: ImportStatsItemToDb = ImportStatsItemToDb(  # type:ignore
            stat_id=str(uuid.uuid4()),
            date=self.update_date,
            parent_id=item_dict.pop("parentId"),
            **item_dict,
        )
        return res

    async def _get_items_to_upload(
        self,
    ) -> Tuple[list[ImportItemToDb], list[ImportStatsItemToDb], list[str]]:
        """
        returns data_to_upload -- list of dictionaries

        Go through all import items
        If parent not in database, but in list of imports,
           then upload parent and then initial item
        elif in database, then
        """
        assert self._ids_already_in_db is not None
        assert self._all_import_items_by_id is not None

        data_to_upload: list[ImportItemToDb] = []
        stats_data_to_upload: list[ImportStatsItemToDb] = []
        all_parent_ids_of_offers: list[str] = []
        ids_uploaded: list[str] = []
        for import_item in self.items_to_import:
            item_id = str(import_item.id)
            if item_id in ids_uploaded:
                continue

            if import_item.type == ItemType.offer.value:
                # save to statistic table
                all_parent_ids_of_offers.extend(
                    await get_all_parent_ids_by_item_id(item_id)
                )
                stats_data_to_upload.append(self._get_stat_item_to_upload(import_item))

            if import_item.parentId is not None and (
                parent_id := str(import_item.parentId)
            ):
                if parent_id in self._ids_already_in_db:
                    data_to_upload.append(self._get_item_to_upload(import_item))
                    ids_uploaded.append(item_id)
                else:  # parent in batch of imports
                    if (
                        parent_id not in ids_uploaded
                    ):  # if not added parent to data to upload yet
                        parent_item = self._all_import_items_by_id[parent_id]
                        data_to_upload.append(self._get_item_to_upload(parent_item))
                        ids_uploaded.append(parent_id)
                    data_to_upload.append(self._get_item_to_upload(import_item))
                    ids_uploaded.append(item_id)
            else:
                data_to_upload.append(self._get_item_to_upload(import_item))
                ids_uploaded.append(item_id)

        del ids_uploaded
        return data_to_upload, stats_data_to_upload, all_parent_ids_of_offers

    async def import_to_db(self) -> None:
        async_checks = AsyncChecks(items=self.items_to_import)
        await async_checks.check()

        await self.__prepare_data()

        (
            items_to_upload,
            stats_items_to_upload,
            all_parent_ids_of_offers,
        ) = await self._get_items_to_upload()
        async with database.transaction():
            await upsert_items(items=items_to_upload)
            await save_import_items_to_statistic(items=stats_items_to_upload)
            await update_date(
                item_ids=all_parent_ids_of_offers, new_update_date=self.update_date
            )


# class RecursiveSQLWithPythonItems:
#     def __init__(self, item_id: str):
#         self.item_id: str = item_id
#         self.prices_or_child_cats_by_item_id: dict[
#             str, list[Union[int, str]]
#         ] = defaultdict(list)
#
#     def _get_recursive_items_for_item(self, item: Item):
#         if item.type == "OFFER":
#             self.prices_or_child_cats_by_item_id[str(item.parent_id)].append(
#                 item.price)
#             return serialize_offer(item)
#
#         if item.parent_id:
#             self.prices_or_child_cats_by_item_id[str(item.parent_id)].append(
#                 str(item.id))
#
#         item_children: QuerySet[Item]
#         if not (item_children := item.children.all()):
#             return serialize_category(item)
#
#         if item_children[0].type == "OFFER":
#             children = []
#             for child_cat in item_children:
#                 self.prices_or_child_cats_by_item_id[str(item.id)].append(
#                     child_cat.price)
#                 children.append(serialize_offer(child_cat))
#         else:
#             children = []
#             for child_cat in item_children:
#                 self.prices_or_child_cats_by_item_id[str(item.id)].append(
#                     str(child_cat.id)
#                 )
#                 children.append(
#                     serialize_category(
#                         category=child_cat,
#                         children=[
#                             self._get_recursive_items_for_item(
#                                 child_child,
#                             )
#                             for child_child in child_cat.children.all()
#                         ],
#                     )
#                 )
#         return serialize_category(category=item, children=children)
#
#     def get(self):
#         if not (item := Item.objects.filter(id=self.item_id).first()):
#             return None
#
#         if item.type == "OFFER":
#             return serialize_offer(offer=item)
#
#         return self._get_recursive_items_for_item(item)
