from psycopg.rows import class_row

from ..base_repository import BaseRepository, RepositoryModel


class CurrencyCategory(RepositoryModel):
    currency_category_id: int
    api_id: str
    label: str


async def get_all_currency_categories() -> list[CurrencyCategory]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(CurrencyCategory)) as cursor:
        query = """
            SELECT currency_category_id, api_id, label FROM currency_category
        """

        await cursor.execute(query)

        return await cursor.fetchall()


class GetAllCurrencyCategories(BaseRepository):
    async def execute(self) -> list[CurrencyCategory]:
        return await get_all_currency_categories()
