from ..base_repository import BaseRepository, scalar_as
from pydantic import BaseModel


class CreateItemCategoryModel(BaseModel):
    id: str
    label: str


class CreateItemCategory(BaseRepository):
    async def execute(self, itemCategory: CreateItemCategoryModel) -> int:
        async with self.get_db_cursor(rowFactory=scalar_as(int)) as cursor:

            query = """
                INSERT INTO "ItemCategory" ("apiId", "label")
                VALUES (%s, %s)
                RETURNING "id"
            """

            await cursor.execute(
                query, (itemCategory.id, itemCategory.label)
            )

            return await anext(cursor)
