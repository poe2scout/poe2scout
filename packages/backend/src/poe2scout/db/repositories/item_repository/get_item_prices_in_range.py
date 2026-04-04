from datetime import datetime
from decimal import Decimal

from psycopg.rows import class_row

from ..base_repository import BaseRepository, RepositoryModel


class GetItemPricesInRangeModel(RepositoryModel):
    item_id: int
    price: Decimal
    quantity: Decimal


async def get_item_prices_in_range(
    item_ids: list[int],
    league_id: int,
    start_time: datetime,
    end_time: datetime,
) -> list[GetItemPricesInRangeModel]:
    async with BaseRepository.get_db_cursor(
        row_factory=class_row(GetItemPricesInRangeModel)
    ) as cursor:
        query = """
            WITH first_price AS (
                SELECT DISTINCT ON (item_id)
                       item_id,
                       price,
                       quantity
                  FROM price_log
                 WHERE league_id = %(league_id)s
                   AND created_at >= %(start_time)s
                   AND created_at < %(end_time)s
                   AND item_id = ANY(%(item_ids)s)
                 ORDER BY item_id, created_at ASC
            )
            SELECT
                req_item.item_id AS item_id,
                COALESCE(fp.price, 0) AS price,
                COALESCE(fp.quantity, 0) AS quantity
              FROM UNNEST(%(item_ids)s) AS req_item(item_id)
              LEFT JOIN first_price AS fp ON req_item.item_id = fp.item_id;
        """
        params = {
            "item_ids": item_ids,
            "league_id": league_id,
            "start_time": start_time,
            "end_time": end_time,
        }
        await cursor.execute(query, params)

        return await cursor.fetchall()
