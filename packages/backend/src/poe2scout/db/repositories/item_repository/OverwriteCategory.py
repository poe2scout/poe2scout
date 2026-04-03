from ..base_repository import BaseRepository


class OverwriteCategory(BaseRepository):
    async def execute(self, categoryId: int, newCategoryId: int):
        async with self.get_db_cursor() as cursor:
            query = """
                UPDATE "ItemType" as it
                SET "categoryId" = %(newCategoryId)s
                Where "categoryId" = %(categoryId)s
            """

            await cursor.execute(
                query, {"categoryId": categoryId, "newCategoryId": newCategoryId}
            )

            return
