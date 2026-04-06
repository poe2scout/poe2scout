from psycopg.rows import class_row

from ..base_repository import BaseRepository, RepositoryModel


class GetItemPricesModel(RepositoryModel):
    item_id: int
    price: float


async def get_item_prices(
        item_ids: list[int], 
        league_id: int,
        realm_id: int) -> list[GetItemPricesModel]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(GetItemPricesModel)) as cursor:
        query = """
            WITH latest_prices AS (
                SELECT DISTINCT ON (item_id)
                       item_id,
                       price
                  FROM price_log
                 WHERE item_id = ANY(%(item_ids)s)
                   AND league_id = %(league_id)s
                   AND realm_id = %(realm_id)s
                 ORDER BY item_id, created_at DESC
            )
            SELECT
                req_item.item_id AS item_id,
                COALESCE(lp.price, 0) AS price
              FROM UNNEST(%(item_ids)s) AS req_item(item_id)
              LEFT JOIN latest_prices AS lp ON req_item.item_id = lp.item_id;
        """

        params = {
            "item_ids": item_ids, 
            "league_id": league_id,
            "realm_id": realm_id
        }
        await cursor.execute(query, params)

        return await cursor.fetchall()
