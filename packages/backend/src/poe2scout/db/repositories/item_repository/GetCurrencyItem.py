from psycopg.rows import class_row

from poe2scout.db.repositories.models import CurrencyItem
from ..base_repository import BaseRepository
from pydantic import BaseModel

class GetCurrencyItemIdModel(BaseModel):
    apiId: str

class GetCurrencyItem(BaseRepository):
    async def execute(self, apiId: str) -> CurrencyItem | None:
        async with self.get_db_cursor(rowFactory=class_row(CurrencyItem)) as cursor:

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
                WHERE ci."apiId" = %{apiId}s
            """

            params = {"apiId": apiId}

            await cursor.execute(query, params)

            return await cursor.fetchone()
