from typing import List

from psycopg.rows import class_row
from ..base_repository import BaseRepository
from pydantic import BaseModel


class Item(BaseModel):
    id: int
    baseItemId: int
    itemType: str


class GetAllItems(BaseRepository):
    async def execute(self) -> List[Item]:
        async with self.get_db_cursor(
            rowFactory=class_row(Item)
        ) as cursor:
            query = """
                SELECT "id", "baseItemId", "itemType" 
                FROM "Item"
            """

            await cursor.execute(query)

            return await cursor.fetchall()
