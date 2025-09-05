from datetime import datetime
from decimal import Decimal
from typing import List
from ..base_repository import BaseRepository
from pydantic import BaseModel
from psycopg.rows import class_row

class GetItemPricesInRangeModel(BaseModel):
    ItemId: int
    Price: Decimal
    Quantity: Decimal

class GetItemPricesInRange(BaseRepository):
    async def execute(self, itemIds: list[int], leagueId: int, startTime: datetime, endTime: datetime) -> List[GetItemPricesInRangeModel]:
        async with self.get_db_cursor(rowFactory=class_row(GetItemPricesInRangeModel)) as cursor:
            query = """
                WITH "FirstPrice" AS (
                    SELECT DISTINCT ON ("itemId")
                           "itemId",
                           "price",
                           "quantity"
                      FROM "PriceLog"
                     WHERE "leagueId" = %(leagueId)s
                       AND "createdAt" >= %(startTime)s
                       AND "createdAt" < %(endTime)s
                       AND "itemId" = ANY(%(itemIds)s)
                     ORDER BY "itemId", "createdAt" ASC
                )
                SELECT
                    req_item."id" AS "ItemId",
                    COALESCE(fp."price", 0) AS "Price",
                    COALESCE(fp."quantity", 0) AS "Quantity"
                  FROM UNNEST(%(itemIds)s) AS req_item("id")
                  LEFT JOIN "FirstPrice" AS fp ON req_item."id" = fp."itemId";
            """        
            params = {
            "itemIds": itemIds,
            "leagueId": leagueId,
            "startTime": startTime,
            "endTime": endTime,
            }
            await cursor.execute(query, params)

            return await cursor.fetchall()