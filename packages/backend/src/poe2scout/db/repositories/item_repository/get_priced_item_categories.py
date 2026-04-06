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
            SELECT ic.item_category_id
                 , ic.api_id
                 , ic.label
             FROM item_category AS ic
             WHERE EXISTS (
                       SELECT 1
                         FROM item_type AS it
                         JOIN base_item AS bi
                           ON bi.item_type_id = it.item_type_id
                         JOIN item AS i
                           ON i.base_item_id = bi.base_item_id
                         JOIN unique_item AS ui
                           ON ui.item_id = i.item_id
                         JOIN price_log AS pl
                           ON pl.item_id = ui.item_id
                        WHERE it.item_category_id = ic.item_category_id
                          AND bi.game_id = %(game_id)s
                          AND pl.league_id = %(league_id)s
                          AND pl.realm_id = %(realm_id)s
                   )
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
