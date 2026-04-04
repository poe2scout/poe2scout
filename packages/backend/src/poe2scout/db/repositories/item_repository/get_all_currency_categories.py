from psycopg.rows import class_row

from poe2scout.db.repositories.item_repository.get_all_item_categories import ItemCategory

from ..base_repository import BaseRepository


async def get_all_currency_categories() -> list[ItemCategory]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(ItemCategory)) as cursor:
        query = """
            SELECT "id", "apiId", "label" FROM "CurrencyCategory"
        """

        await cursor.execute(query)

        return await cursor.fetchall()


class GetAllCurrencyCategories(BaseRepository):
    async def execute(self) -> list[ItemCategory]:
        return await get_all_currency_categories()
