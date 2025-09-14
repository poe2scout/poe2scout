from typing import Awaitable
from ..base_repository import BaseRepository
from pydantic import BaseModel


class GetUniqueItemIdModel(BaseModel):
    name: str


class GetUniqueItemId(BaseRepository):
    async def execute(self, name: str) -> Awaitable[int]:
        item_query = """
            SELECT "itemId" FROM "UniqueItem"
            WHERE "name" = %s
        """

        uniqueItemId = (await self.execute_query(item_query, (name,)))[0]["itemId"]

        return uniqueItemId
