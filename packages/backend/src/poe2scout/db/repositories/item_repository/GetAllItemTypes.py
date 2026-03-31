from typing import List
from ..base_repository import BaseRepository
from pydantic import BaseModel


class ItemType(BaseModel):
    id: int
    value: str
    categoryId: int


class GetAllItemTypes(BaseRepository):
    async def execute(self) -> List[ItemType]:
        itemType_query = """
            SELECT "id", "value", "categoryId" FROM "ItemType"
        """

        itemTypes = await self.execute_query(itemType_query)

        return [ItemType(**itemType) for itemType in itemTypes]
