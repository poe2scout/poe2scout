from ..base_repository import BaseRepository, scalar_as
from pydantic import BaseModel


class CreateItemModel(BaseModel):
    baseItemId: int
    itemType: str  # 'unique' or 'currency'

class CreateItem(BaseRepository):
    async def execute(self, item: CreateItemModel) -> int:
        async with self.get_db_cursor(rowFactory=scalar_as(int)) as cursor:

            query = """
                INSERT INTO "Item" ("baseItemId", "itemType")
                VALUES (%s, %s)
                RETURNING "id"
            """

            await cursor.execute(query, (item.baseItemId, item.itemType))

            return await anext(cursor)
