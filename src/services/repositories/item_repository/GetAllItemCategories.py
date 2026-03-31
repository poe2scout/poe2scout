from typing import List
from ..base_repository import BaseRepository
from pydantic import BaseModel


class ItemCategory(BaseModel):
    id: int
    apiId: str
    label: str


class GetAllItemCategories(BaseRepository):
    async def execute(self) -> List[ItemCategory]:
        itemCategory_query = """
            SELECT "id", "apiId", "label" FROM "ItemCategory"
        """

        itemCategories = await self.execute_query(itemCategory_query)

        return [ItemCategory(**itemCategory) for itemCategory in itemCategories]
