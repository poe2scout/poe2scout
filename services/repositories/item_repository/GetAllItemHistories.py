import itertools
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, List

from pydantic import BaseModel
from psycopg.rows import class_row

from services.repositories.item_repository.GetAllItems import Item
from ..base_repository import BaseRepository


class ItemHistoryLog(BaseModel):
    Price: Decimal
    Time: datetime
    Quantity: int


class ItemHistory(BaseModel):
    ItemId: int
    History: List[ItemHistoryLog]


class _AllItemHistoriesRow(BaseModel):
    ItemId: int
    Time: datetime
    Price: Decimal
    Quantity: int


class GetAllItemHistories(BaseRepository):
    async def execute(self, leagueId: int) -> List[ItemHistory]:
        async with self.get_db_cursor(rowFactory=class_row(_AllItemHistoriesRow)) as cursor:
            query = """
WITH ranked_logs AS (
    SELECT "itemId",
           price,
           quantity,
           "createdAt",
            ROW_NUMBER() OVER (
                PARTITION BY "itemId"
                ORDER BY "createdAt" DESC) AS rn
      FROM "PriceLog"
     WHERE "leagueId" = %(leagueId)s)
SELECT "itemId" AS "ItemId",
       "createdAt" AS "Time",
       price AS "Price",
       quantity AS "Quantity"
  FROM ranked_logs
 WHERE rn <= 24
 ORDER BY "ItemId", "Time" DESC;
            """
            params = {
                "leagueId": leagueId
            }

            await cursor.execute(query, params)
            rows: List[_AllItemHistoriesRow] = await cursor.fetchall()

            if not rows:
                return []
            
            three_dp = Decimal('0.001')

            result = [
                ItemHistory.model_construct(
                    ItemId=item_id,
                    History=[
                        ItemHistoryLog.model_construct(
                            Price=row.Price.quantize(three_dp, rounding=ROUND_HALF_UP),
                            Time=row.Time,
                            Quantity=row.Quantity
                        ) for row in group
                    ]
                )
                for item_id, group in itertools.groupby(rows, key=lambda r: r.ItemId)
            ]

            return result