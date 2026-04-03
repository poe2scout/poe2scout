from typing import List

from psycopg.rows import class_row
from ..base_repository import BaseRepository
from pydantic import BaseModel


class ItemType(BaseModel):
    id: int
    value: str
    categoryId: int


class GetAllItemTypes(BaseRepository):
    async def execute(self) -> List[ItemType]:
        async with self.get_db_cursor(
            rowFactory=class_row(ItemType)
        ) as cursor:
            query = """
                SELECT "id", "value", "categoryId" FROM "ItemType"
            """

            await cursor.execute(query)

            return await cursor.fetchall()
