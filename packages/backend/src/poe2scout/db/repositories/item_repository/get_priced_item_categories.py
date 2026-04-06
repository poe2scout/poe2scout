from psycopg.rows import class_row

from ..base_repository import BaseRepository
from .get_all_item_categories import ItemCategory


async def get_priced_item_categories(
    league_id: int,
    realm_id: int,
    game_id: int,
) -> list[ItemCategory]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(ItemCategory)) as cursor:
        query = """
            WITH priced_items AS (
                SELECT DISTINCT pl.item_id
                  FROM price_log AS pl
                 WHERE pl.league_id = %(league_id)s
                   AND pl.realm_id = %(realm_id)s
            )
            SELECT ic.item_category_id
                 , ic.api_id
                 , ic.label
             FROM item_category AS ic
             JOIN item_type AS it
               ON it.item_category_id = ic.item_category_id
             JOIN base_item AS bi
               ON bi.item_type_id = it.item_type_id
             JOIN item AS i
               ON i.base_item_id = bi.base_item_id
             JOIN unique_item AS ui
               ON ui.item_id = i.item_id
             JOIN priced_items AS pi
               ON pi.item_id = ui.item_id
            WHERE bi.game_id = %(game_id)s
            GROUP BY ic.item_category_id, ic.api_id, ic.label
             ORDER BY ic.item_category_id
        """

        params = {
            "league_id": league_id,
            "realm_id": realm_id,
            "game_id": game_id,
        }

        await cursor.execute(query, params)

        return await cursor.fetchall()


class GetPricedItemCategories(BaseRepository):
    async def execute(
        self,
        league_id: int,
        realm_id: int,
        game_id: int,
    ) -> list[ItemCategory]:
        return await get_priced_item_categories(league_id, realm_id, game_id)
