from typing import List
from ..base_repository import BaseRepository
from pydantic import BaseModel


class Item(BaseModel):
    id: int
    baseItemId: int
    itemType: str


class GetAllItems(BaseRepository):
    async def execute(self) -> List[Item]:
        item_query = """
            SELECT "id", "baseItemId", "itemType" 
            FROM "Item"
        """

        items = await self.execute_query(item_query)

        return [Item(**item) for item in items]
