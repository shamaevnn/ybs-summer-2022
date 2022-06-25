from typing import Optional, cast

from app.models.items.queries import get_items_tree_with_additional_info
from app.types import DbItemWithAddInfo, ItemType, ItemsOut


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

    async def get(self) -> Optional[ItemsOut]:
        _db_tree: Optional[DbItemWithAddInfo] = await get_items_tree_with_additional_info(
            self.start_item_id
        )
        if not _db_tree:
            return None
        db_tree: ItemsOut = self._set_price_and_del_ambiguous_values(_db_tree)
        return db_tree


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
