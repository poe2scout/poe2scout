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
            WITH "FirstPrice" AS (
                SELECT DISTINCT ON ("itemId")
                       "itemId",
                       "price",
                       "quantity"
                  FROM "PriceLog"
                 WHERE "leagueId" = %(league_id)s
                   AND "createdAt" >= %(start_time)s
                   AND "createdAt" < %(end_time)s
                   AND "itemId" = ANY(%(item_ids)s)
                 ORDER BY "itemId", "createdAt" ASC
            )
            SELECT
                req_item."id" AS "item_id",
                COALESCE(fp."price", 0) AS "price",
                COALESCE(fp."quantity", 0) AS "quantity"
              FROM UNNEST(%(item_ids)s) AS req_item("id")
              LEFT JOIN "FirstPrice" AS fp ON req_item."id" = fp."itemId";
        """
        params = {
            "item_ids": item_ids,
            "league_id": league_id,
            "start_time": start_time,
            "end_time": end_time,
        }
        await cursor.execute(query, params)

        return await cursor.fetchall()