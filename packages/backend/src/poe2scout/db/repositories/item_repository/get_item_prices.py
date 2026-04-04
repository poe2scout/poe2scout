from psycopg.rows import class_row

from ..base_repository import BaseRepository, RepositoryModel


class GetItemPricesModel(RepositoryModel):
    item_id: int
    price: float


async def get_item_prices(item_ids: list[int], league_id: int) -> list[GetItemPricesModel]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(GetItemPricesModel)) as cursor:
        query = """
            WITH "LatestPrices" AS (
                SELECT DISTINCT ON ("itemId")
                       "itemId",
                       "price"
                  FROM "PriceLog"
                 WHERE "itemId" = ANY(%(item_ids)s)
                   AND "leagueId" = %(league_id)s
                 ORDER BY "itemId", "createdAt" DESC
            )
            SELECT
                req_item."id" AS "item_id",
                COALESCE(lp."price", 0) AS "price"
              FROM UNNEST(%(item_ids)s) AS req_item("id")
              LEFT JOIN "LatestPrices" AS lp ON req_item."id" = lp."itemId";
        """

        params = {"item_ids": item_ids, "league_id": league_id}
        await cursor.execute(query, params)

        return await cursor.fetchall()
