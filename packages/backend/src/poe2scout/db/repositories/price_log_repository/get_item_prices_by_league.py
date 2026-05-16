from psycopg.rows import class_row

from ..base_repository import BaseRepository, RepositoryModel


class GetItemPricesByLeagueModel(RepositoryModel):
    league_id: int
    item_id: int
    price: float


async def get_item_prices_by_league(
    item_ids: list[int],
    league_ids: list[int],
    realm_id: int,
) -> list[GetItemPricesByLeagueModel]:
    async with BaseRepository.get_db_cursor(
        row_factory=class_row(GetItemPricesByLeagueModel)
    ) as cursor:
        query = """
            WITH requested_prices AS (
                SELECT req_league.league_id
                     , req_item.item_id
                  FROM UNNEST(%(league_ids)s) AS req_league(league_id)
                 CROSS JOIN UNNEST(%(item_ids)s) AS req_item(item_id)
            )
            SELECT requested_prices.league_id
                 , requested_prices.item_id
                 , COALESCE(latest_price.price, 0) AS price
              FROM requested_prices
              LEFT JOIN LATERAL (
                  SELECT price
                    FROM price_log
                   WHERE item_id = requested_prices.item_id
                     AND league_id = requested_prices.league_id
                     AND realm_id = %(realm_id)s
                   ORDER BY created_at DESC
                   LIMIT 1
              ) AS latest_price ON TRUE;
        """

        params = {
            "item_ids": item_ids,
            "league_ids": league_ids,
            "realm_id": realm_id,
        }
        await cursor.execute(query, params)

        return await cursor.fetchall()
