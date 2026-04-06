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
            SELECT cc.currency_category_id
                 , cc.api_id
                 , cc.label
             FROM currency_category AS cc
             WHERE EXISTS (
                       SELECT 1
                         FROM currency_item AS ci
                         JOIN item AS i
                           ON i.item_id = ci.item_id
                         JOIN base_item AS bi
                           ON bi.base_item_id = i.base_item_id
                         JOIN price_log AS pl
                           ON pl.item_id = ci.item_id
                        WHERE ci.currency_category_id = cc.currency_category_id
                          AND bi.game_id = %(game_id)s
                          AND pl.league_id = %(league_id)s
                          AND pl.realm_id = %(realm_id)s
                   )
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
