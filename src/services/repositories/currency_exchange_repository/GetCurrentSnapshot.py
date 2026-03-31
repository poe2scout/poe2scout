from decimal import Decimal
from ..base_repository import BaseRepository
from pydantic import BaseModel
from psycopg.rows import class_row


class GetCurrencyExchangeModel(BaseModel):
    Epoch: int
    Volume: Decimal
    MarketCap: Decimal


class GetCurrencyExchange(BaseRepository):
    async def execute(self, leagueId: int) -> GetCurrencyExchangeModel | None:
        async with self.get_db_cursor(
            rowFactory=class_row(GetCurrencyExchangeModel)
        ) as cursor:
            query = """
                SELECT "Epoch",
                       "Volume",
                       "MarketCap"
                  FROM "CurrencyExchangeSnapshot"
                 WHERE "LeagueId" = %(leagueId)s
                 ORDER BY "Epoch" DESC
                 LIMIT 1
            """

            params = {"leagueId": leagueId}

            await cursor.execute(query, params)

            return await cursor.fetchone()
