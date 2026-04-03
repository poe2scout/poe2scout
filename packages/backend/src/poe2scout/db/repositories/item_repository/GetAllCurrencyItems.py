from typing import List

from psycopg.rows import class_row

from poe2scout.db.repositories.models import CurrencyItem
from ..base_repository import BaseRepository


class GetAllCurrencyItems(BaseRepository):
    async def execute(self) -> List[CurrencyItem]:
        async with self.get_db_cursor(
            rowFactory=class_row(CurrencyItem)
        ) as cursor:
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
