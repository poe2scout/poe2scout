from psycopg.rows import class_row

from poe2scout.db.repositories.models import CurrencyItem

from ..base_repository import BaseRepository, RepositoryModel


class GetCurrencyItemIdModel(RepositoryModel):
    api_id: str


async def get_currency_item(api_id: str) -> CurrencyItem | None:
    async with BaseRepository.get_db_cursor(row_factory=class_row(CurrencyItem)) as cursor:
        query = """
            SELECT ci."id",
                ci."itemId",
                ci."apiId",
                ci."text",
                ci."iconUrl",
                ci."currencyCategoryId",
                cc."label",
                cc."apiId" as "categoryApiId"
            FROM "CurrencyItem" as ci
            JOIN "CurrencyCategory" as cc on ci."currencyCategoryId" = cc."id"
            WHERE ci."apiId" = %(api_id)s
        """

        params = {"api_id": api_id}

        await cursor.execute(query, params)

        return await cursor.fetchone()


class GetCurrencyItem(BaseRepository):
    async def execute(self, api_id: str) -> CurrencyItem | None:
        return await get_currency_item(api_id)
