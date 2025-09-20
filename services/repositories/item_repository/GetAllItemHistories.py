import itertools
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import List

from pydantic import BaseModel
from psycopg.rows import class_row

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
        async with self.get_db_cursor(
            rowFactory=class_row(_AllItemHistoriesRow)
        ) as cursor:
            query = """
WITH RECURSIVE distinct_items AS (
    (SELECT "itemId"
       FROM "PriceLog"
      WHERE "leagueId" = %(leagueId)s
      ORDER BY "itemId"
      LIMIT 1)

     UNION ALL

    SELECT (
        SELECT "itemId"
          FROM "PriceLog"
         WHERE "leagueId" = 5 AND "itemId" > di."itemId"
         ORDER BY "itemId"
         LIMIT 1
    )
      FROM distinct_items di
     WHERE di."itemId" IS NOT NULL
)
SELECT p."itemId" AS "ItemId",
       p."createdAt" AS "Time",
       p.price AS "Price",
       p.quantity AS "Quantity"
FROM (
    SELECT "itemId" FROM distinct_items WHERE "itemId" IS NOT NULL
) AS items
CROSS JOIN LATERAL (
    SELECT "createdAt", price, quantity, "itemId"
      FROM "PriceLog"
     WHERE "leagueId" = 5 AND "PriceLog"."itemId" = items."itemId"
     ORDER BY "createdAt" DESC
     LIMIT 24
) AS p
ORDER BY p."itemId", p."createdAt" DESC;
            """
            params = {"leagueId": leagueId}

            await cursor.execute(query, params)
            rows: List[_AllItemHistoriesRow] = await cursor.fetchall()

            if not rows:
                return []

            three_dp = Decimal("0.001")

            result = [
                ItemHistory.model_construct(
                    ItemId=item_id,
                    History=[
                        ItemHistoryLog.model_construct(
                            Price=row.Price.quantize(three_dp, rounding=ROUND_HALF_UP),
                            Time=row.Time,
                            Quantity=row.Quantity,
                        )
                        for row in group
                    ],
                )
                for item_id, group in itertools.groupby(rows, key=lambda r: r.ItemId)
            ]

            return result
