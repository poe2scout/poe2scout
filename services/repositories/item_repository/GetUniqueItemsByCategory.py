from typing import Tuple, Optional, List
from ..base_repository import BaseRepository
from .GetAllUniqueItems import UniqueItem


class GetUniqueItemsByCategory(BaseRepository):
    async def execute(self, category: str) -> List[UniqueItem]:
        uniqueItem_query = """
            SELECT ui."id", ui."itemId", ic."label", ic."apiId" as "categoryApiId", ui."name", ui."text", ui."iconUrl", it."value" as type, ui."itemMetadata" FROM "UniqueItem" AS ui
            JOIN "Item" AS i ON ui."itemId" = i."id"
            JOIN "BaseItem" AS bi ON i."baseItemId" = bi."id"
            JOIN "ItemType" AS it ON bi."typeId" = it."id"
            JOIN "ItemCategory" AS ic ON it."categoryId" = ic."id"
            WHERE ic."apiId" = %s
        """
        params = (category,)

        uniqueItems = await self.execute_query(
            uniqueItem_query, params)

        return [UniqueItem(**uniqueItem) for uniqueItem in uniqueItems]
