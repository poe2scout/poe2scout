from psycopg.rows import class_row

from poe2scout.db.repositories.item_repository.GetAllItemCategories import ItemCategory

from ..base_repository import BaseRepository

class GetAllCurrencyCategories(BaseRepository):
    async def execute(self) -> list[ItemCategory]:
        async with self.get_db_cursor(
            rowFactory=class_row(ItemCategory)
        ) as cursor:
            
            query = """
                SELECT "id", "apiId", "label" FROM "CurrencyCategory"
            """

            await cursor.execute(query)

            return await cursor.fetchall()
