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


async def get_all_item_histories(league_id: int, realm_id: int) -> list[ItemHistory]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(_AllItemHistoriesRow)) as cursor:
        query = """
WITH RECURSIVE distinct_items AS (
    (SELECT item_id
       FROM price_log
      WHERE league_id = %(league_id)s
        AND realm_id = %(realm_id)s
      ORDER BY item_id
      LIMIT 1)

     UNION ALL

    SELECT (
        SELECT item_id
          FROM price_log
         WHERE league_id = %(league_id)s 
           AND item_id > di.item_id
           AND realm_id = %(realm_id)s
         ORDER BY item_id
         LIMIT 1
    )
      FROM distinct_items di
     WHERE di.item_id IS NOT NULL
)
SELECT p.item_id AS "item_id",
       p.created_at AS "time",
       p.price AS "price",
       p.quantity AS "quantity"
FROM (
    SELECT item_id FROM distinct_items WHERE item_id IS NOT NULL
) AS items
CROSS JOIN LATERAL (
    SELECT created_at, price, quantity, item_id
      FROM price_log
     WHERE league_id = %(league_id)s 
       AND realm_id = %(realm_id)s
       AND price_log.item_id = items.item_id
     ORDER BY created_at DESC
     LIMIT 24
) AS p
ORDER BY p.item_id, p.created_at DESC;
        """
        params = {
            "league_id": league_id,
            "realm_id": realm_id
        }

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