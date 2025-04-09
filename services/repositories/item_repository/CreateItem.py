from typing import Optional
from ..base_repository import BaseRepository
from pydantic import BaseModel


class CreateItemModel(BaseModel):
    baseItemId: int
    itemType: str  # 'unique' or 'currency'


class CreateItem(BaseRepository):
    async def execute(self, item: CreateItemModel) -> int:
        item_query = """
            INSERT INTO "Item" ("baseItemId", "itemType")
            VALUES (%s, %s)
            RETURNING "id"
        """

        itemId = await self.execute_single(
            item_query, (item.baseItemId, item.itemType))

        return itemId
