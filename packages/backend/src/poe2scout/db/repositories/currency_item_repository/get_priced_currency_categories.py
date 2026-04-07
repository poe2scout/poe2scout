from psycopg.rows import class_row

from ..base_repository import BaseRepository
from .get_all_currency_categories import CurrencyCategory


async def get_priced_currency_categories(
    league_id: int,
    realm_id: int,
    game_id: int,
) -> list[CurrencyCategory]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(CurrencyCategory)) as cursor:
        query = """
            WITH priced_items AS (
                SELECT DISTINCT ci.currency_category_id
                  FROM currency_item AS ci
                  JOIN item AS i
                    ON i.item_id = ci.item_id
                  JOIN base_item AS bi
                    ON bi.base_item_id = i.base_item_id
                 WHERE bi.game_id = %(game_id)s
                   AND EXISTS (
                       SELECT 1
                         FROM price_log AS pl
                        WHERE pl.league_id = %(league_id)s
                          AND pl.realm_id = %(realm_id)s
                          AND pl.item_id = ci.item_id
                   )
            )
            SELECT cc.currency_category_id
                 , cc.api_id
                 , cc.label
             FROM currency_category AS cc
             JOIN priced_items AS pi
               ON pi.currency_category_id = cc.currency_category_id
             ORDER BY cc.currency_category_id
        """

        params = {
            "league_id": league_id,
            "realm_id": realm_id,
            "game_id": game_id,
        }

        await cursor.execute(query, params)

        return await cursor.fetchall()


class GetPricedCurrencyCategories(BaseRepository):
    async def execute(
        self,
        league_id: int,
        realm_id: int,
        game_id: int,
    ) -> list[CurrencyCategory]:
        return await get_priced_currency_categories(league_id, realm_id, game_id)
