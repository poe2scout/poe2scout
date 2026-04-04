from psycopg.rows import class_row

from poe2scout.db.repositories.models import CurrencyItem

from ..base_repository import BaseRepository


async def get_all_currency_items() -> list[CurrencyItem]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(CurrencyItem)) as cursor:
        query = """
            SELECT ci."id"
                 , ci."itemId"
                 , ci."currencyCategoryId"
                 , cc."apiId" as "categoryApiId"
                 , ci."apiId", ci."text"
                 , ci."iconUrl"
                 , "itemMetadata"
              FROM "CurrencyItem" as ci
              JOIN "CurrencyCategory" as cc on ci."currencyCategoryId" = cc.id
        """

        await cursor.execute(query)

        return await cursor.fetchall()


class GetAllCurrencyItems(BaseRepository):
    async def execute(self) -> list[CurrencyItem]:
        return await get_all_currency_items()
