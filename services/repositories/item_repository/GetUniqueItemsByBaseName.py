from typing import Tuple, Optional, List
from ..base_repository import BaseRepository
from .GetAllUniqueItems import UniqueItem


class GetUniqueItemsByBaseName(BaseRepository):
    async def execute(self, baseName: str) -> List[UniqueItem]:
        uniqueItem_query = """
            SELECT ui."id", ui."itemId", ui."name", ui."text", ic."apiId" as "categoryApiId", ui."iconUrl", it."value" as type, ui."itemMetadata" 
            FROM "UniqueItem" AS ui
            JOIN "Item" AS i ON ui."itemId" = i."id"
            JOIN "BaseItem" AS bi ON i."baseItemId" = bi."id"
            JOIN "ItemType" AS it ON bi."typeId" = it."id"
            JOIN "ItemCategory" AS ic ON it."categoryId" = ic."id"
            WHERE it."value" = %s
        """
        uniqueItems = await self.execute_query(
            uniqueItem_query, (baseName,))

        return [UniqueItem(**uniqueItem) for uniqueItem in uniqueItems]
