from typing import List

from psycopg.rows import class_row

from poe2scout.db.repositories.models import CurrencyItem
from ..base_repository import BaseRepository


class GetCurrencyItemsByCategory(BaseRepository):
    async def execute(self, category: str) -> List[CurrencyItem]:
        async with self.get_db_cursor(
            rowFactory=class_row(CurrencyItem)
        ) as cursor:

            query = """
                SELECT ci."id"
                    , ci."itemId"
                    , cc."label"
                    , cc."apiId" as "categoryApiId"
                    , ci."apiId", ci."text"
                    , ci."iconUrl"
                    , ci."currencyCategoryId"
                    , ci."itemMetadata" 
                FROM "CurrencyItem" AS ci
                JOIN "CurrencyCategory" AS cc ON ci."currencyCategoryId" = cc."id"
                WHERE cc."apiId" ILIKE %s
            """
            params = (category,)

            await cursor.execute(query, params)

            return await cursor.fetchall()
