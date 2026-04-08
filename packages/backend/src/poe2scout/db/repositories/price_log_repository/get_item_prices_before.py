from psycopg.rows import class_row

from ..base_repository import BaseRepository, RepositoryModel


class GetItemPricesBeforeModel(RepositoryModel):
    item_id: int
    price: float


async def get_item_prices_before(
    item_ids: list[int],
    league_id: int,
    realm_id: int,
    epoch: int,
) -> list[GetItemPricesBeforeModel]:
    async with BaseRepository.get_db_cursor(
        row_factory=class_row(GetItemPricesBeforeModel)
    ) as cursor:
        query = """
            SELECT
                req_item.item_id AS item_id,
                COALESCE(latest_price.price, 0) AS price
              FROM UNNEST(%(item_ids)s) AS req_item(item_id)
              LEFT JOIN LATERAL (
                  SELECT price
                    FROM price_log
                   WHERE item_id = req_item.item_id
                     AND league_id = %(league_id)s
                     AND realm_id = %(realm_id)s
                     AND created_at < to_timestamp(%(created_at)s)
                   ORDER BY created_at DESC
                   LIMIT 1
              ) AS latest_price ON TRUE;
        """

        params = {
            "item_ids": item_ids,
            "league_id": league_id,
            "realm_id": realm_id,
            "created_at": epoch,
        }
        await cursor.execute(query, params)

        return await cursor.fetchall()
