import itertools
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from psycopg.rows import class_row

from ..base_repository import BaseRepository, RepositoryModel


class ItemHistoryLog(RepositoryModel):
    price: Decimal
    time: datetime
    quantity: int


class ItemHistory(RepositoryModel):
    item_id: int
    history: list[ItemHistoryLog]


class _AllItemHistoriesRow(RepositoryModel):
    item_id: int
    time: datetime
    price: Decimal
    quantity: int


async def get_all_item_histories(league_id: int) -> list[ItemHistory]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(_AllItemHistoriesRow)) as cursor:
        query = """
WITH RECURSIVE distinct_items AS (
    (SELECT "itemId"
       FROM "PriceLog"
      WHERE "leagueId" = %(league_id)s
      ORDER BY "itemId"
      LIMIT 1)

     UNION ALL

    SELECT (
        SELECT "itemId"
          FROM "PriceLog"
         WHERE "leagueId" = %(league_id)s AND "itemId" > di."itemId"
         ORDER BY "itemId"
         LIMIT 1
    )
      FROM distinct_items di
     WHERE di."itemId" IS NOT NULL
)
SELECT p."itemId" AS "item_id",
       p."createdAt" AS "time",
       p.price AS "price",
       p.quantity AS "quantity"
FROM (
    SELECT "itemId" FROM distinct_items WHERE "itemId" IS NOT NULL
) AS items
CROSS JOIN LATERAL (
    SELECT "createdAt", price, quantity, "itemId"
      FROM "PriceLog"
     WHERE "leagueId" = %(league_id)s AND "PriceLog"."itemId" = items."itemId"
     ORDER BY "createdAt" DESC
     LIMIT 24
) AS p
ORDER BY p."itemId", p."createdAt" DESC;
        """
        params = {"league_id": league_id}

        await cursor.execute(query, params)
        rows = await cursor.fetchall()

        if not rows:
            return []

        three_dp = Decimal("0.001")

        return [
            ItemHistory.model_construct(
                item_id=item_id,
                history=[
                    ItemHistoryLog.model_construct(
                        price=row.price.quantize(three_dp, rounding=ROUND_HALF_UP),
                        time=row.time,
                        quantity=row.quantity,
                    )
                    for row in group
                ],
            )
            for item_id, group in itertools.groupby(rows, key=lambda row: row.item_id)
        ]


class GetAllItemHistories(BaseRepository):
    async def execute(self, league_id: int) -> list[ItemHistory]:
        return await get_all_item_histories(league_id)
