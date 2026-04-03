from typing import List

from psycopg.rows import class_row
from ..base_repository import BaseRepository
from pydantic import BaseModel


class ItemCategory(BaseModel):
    id: int
    apiId: str
    label: str


class GetAllItemCategories(BaseRepository):
    async def execute(self) -> List[ItemCategory]:
        async with self.get_db_cursor(
            rowFactory=class_row(ItemCategory)
        ) as cursor:

            query = """
                SELECT "id", "apiId", "label" FROM "ItemCategory"
            """

            await cursor.execute(query)

            return await cursor.fetchall()
