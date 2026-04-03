from psycopg.rows import dict_row

from ..base_repository import BaseRepository


class IsItemACurrency(BaseRepository):
    async def execute(self, itemId: int) -> bool:
        async with self.get_db_cursor(
            rowFactory=dict_row
        ) as cursor:
            query = """
                SELECT ci."id"
                    , ci."itemId"
                    , ci."apiId"
                    , ci."text"
                    , ci."iconUrl"
                    , ci."currencyCategoryId"
                    , cc."label"
                    , cc."apiId" as "categoryApiId" 
                FROM "CurrencyItem" as ci
                JOIN "CurrencyCategory" as cc on ci."currencyCategoryId" = cc."id"
                WHERE ci."itemId" = %s
            """

            await cursor.execute(query, (itemId,))

            return len(await cursor.fetchall()) == 1
