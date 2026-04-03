from ..base_repository import BaseRepository, scalar_as
from pydantic import BaseModel


class CreateItemTypeModel(BaseModel):
    value: str
    categoryId: int


class CreateItemType(BaseRepository):
    async def execute(self, itemType: CreateItemTypeModel) -> int:
        async with self.get_db_cursor(rowFactory=scalar_as(int)) as cursor:

            query = """
                INSERT INTO "ItemType" ("value", "categoryId")
                VALUES (%s, %s)
                RETURNING "id"
            """

            await cursor.execute(
                query, (itemType.value, itemType.categoryId)
            )

            return await anext(cursor)
