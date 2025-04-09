from typing import Tuple, Optional, List
from ..base_repository import BaseRepository
from pydantic import BaseModel

class UniqueItem(BaseModel):
    id: int
    itemId: int
    iconUrl: Optional[str] = None
    text: str
    name: str
    categoryApiId: str
    itemMetadata: Optional[dict] = None
    type: str


class GetAllUniqueItems(BaseRepository):
    async def execute(self) -> List[UniqueItem]:
        uniqueItem_query = """
            SELECT ui."id", ui."itemId", ui."iconUrl", ui."text", ui."name", ui."itemMetadata", it."value" as "type", ic."apiId" as "categoryApiId" FROM "UniqueItem" as ui
            JOIN "Item" AS i ON ui."itemId" = i."id"
            JOIN "BaseItem" AS bi ON i."baseItemId" = bi."id"
            JOIN "ItemType" AS it ON bi."typeId" = it."id"
			JOIN "ItemCategory" AS ic on ic."id" = it."categoryId"
        """

        uniqueItems = await self.execute_query(
            uniqueItem_query)

        return [UniqueItem(**uniqueItem) for uniqueItem in uniqueItems]
