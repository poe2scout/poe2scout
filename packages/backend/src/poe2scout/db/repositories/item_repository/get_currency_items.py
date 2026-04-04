from psycopg.rows import class_row

from poe2scout.db.repositories.models import CurrencyItem

from ..base_repository import BaseRepository


async def get_currency_items(api_ids: list[str]) -> list[CurrencyItem]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(CurrencyItem)) as cursor:
        query = """
SELECT ci."id"
    , ci."itemId"
    , ci."apiId"
    , ci."text"
    , ci."iconUrl"
    , ci."currencyCategoryId"
    , cc."label"
    , cc."apiId" AS "categoryApiId"
FROM "CurrencyItem" AS ci
JOIN "CurrencyCategory" AS cc ON ci."currencyCategoryId" = cc."id"
WHERE ci."apiId" = ANY(%s)
        """

        await cursor.execute(query, (api_ids,))

        return await cursor.fetchall()
