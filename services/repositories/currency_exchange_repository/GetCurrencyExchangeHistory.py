from decimal import Decimal
from typing import List
from ..base_repository import BaseRepository
from pydantic import BaseModel
from psycopg.rows import class_row

class GetCurrencyExchangeHistoryData(BaseModel):
    Epoch: int
    MarketCap: Decimal
    Volume: Decimal

class GetCurrencyExchangeHistoryModel(BaseModel):
    Data: List[GetCurrencyExchangeHistoryData]
    Meta: dict[str, bool]

class GetCurrencyExchangeHistory(BaseRepository):
    async def execute(self, leagueId: int, endTime: int, limit: int):
        async with self.get_db_cursor(rowFactory=class_row(GetCurrencyExchangeHistoryData)) as cursor:
            query = """
                    SELECT "Epoch",
                           "MarketCap", 
                           "Volume" 
                      FROM "CurrencyExchangeSnapshot"
                     WHERE "LeagueId" = %(leagueId)s 
                           AND "Epoch" < %(endTime)s
                     ORDER BY
                           "Epoch" DESC
                     LIMIT %(limit)s 
            """

            params = {
                "leagueId": leagueId,
                "endTime": endTime,
                "limit": limit+1
            }

            await cursor.execute(query, params)
            
            records = await cursor.fetchall() 

            hasMore = False

            if (len(records) > limit):
                hasMore = True
                records.pop()
            
            records.reverse()
            return GetCurrencyExchangeHistoryModel(Data=records, Meta={"hasMore": hasMore})
