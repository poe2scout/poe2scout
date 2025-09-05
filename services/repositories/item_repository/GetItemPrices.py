from decimal import Decimal
from typing import List, Optional, Awaitable
from ..base_repository import BaseRepository
from pydantic import BaseModel
from psycopg.rows import class_row

class GetItemPricesModel(BaseModel):
    ItemId: int
    Price: float

class GetItemPrices(BaseRepository):
    async def execute(self, itemIds: List[int], leagueId: int):
        async with self.get_db_cursor(rowFactory=class_row(GetItemPricesModel)) as cursor:
            query = """
                WITH "LatestPrices" AS (
                    SELECT DISTINCT ON ("itemId")
                           "itemId",
                           "price" 
                      FROM "PriceLog"
                     WHERE "itemId" = ANY(%(itemIds)s) 
                       AND "leagueId" = %(leagueId)s
                     ORDER BY "itemId", "createdAt" DESC
                )
                SELECT
                    req_item."id" AS "ItemId",
                    COALESCE(lp."price", 0) AS "Price"
                  FROM UNNEST(%(itemIds)s) AS req_item("id")
                  LEFT JOIN "LatestPrices" AS lp ON req_item."id" = lp."itemId";
            """
            
            params = {
                "itemIds": itemIds,
                "leagueId": leagueId
            }
            await cursor.execute(query, params)
            
            return await cursor.fetchall()