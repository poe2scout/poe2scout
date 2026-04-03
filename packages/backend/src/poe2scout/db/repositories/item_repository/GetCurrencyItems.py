
from psycopg.rows import class_row

from poe2scout.db.repositories.models import CurrencyItem
from ..base_repository import BaseRepository


class GetCurrencyItems(BaseRepository):
    async def execute(self, apiIds: list[str]) -> list[CurrencyItem]:
        async with self.get_db_cursor(
            rowFactory=class_row(CurrencyItem)
        ) as cursor:

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

            await cursor.execute(query, (apiIds,))

            return await cursor.fetchall()
