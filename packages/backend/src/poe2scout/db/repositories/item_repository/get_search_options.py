from psycopg.rows import class_row

from ..base_repository import BaseRepository, RepositoryModel


class SearchOption(RepositoryModel):
    display_name: str
    category: str
    identifier: str


async def get_search_options(game_id: int) -> list[SearchOption]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(SearchOption)) as cursor:
        query = """
            SELECT
                ui.name AS display_name,
                ic.api_id AS category,
                ui.name AS identifier
            FROM unique_item ui
            JOIN item i ON ui.item_id = i.item_id
            JOIN base_item bi ON i.base_item_id = bi.base_item_id
            JOIN item_type it ON bi.item_type_id = it.item_type_id
            JOIN item_category ic ON ic.item_category_id = it.item_category_id
            WHERE i.item_type = 'unique'
              AND bi.game_id = %(game_id)s

            UNION ALL

            SELECT
                ci.text AS display_name,
                LOWER(COALESCE(cc.api_id, '')) AS category,
                ci.text AS identifier
            FROM currency_item ci
            JOIN item i ON ci.item_id = i.item_id
            JOIN currency_category cc ON cc.currency_category_id = ci.currency_category_id
            JOIN base_item bi ON i.base_item_id = bi.base_item_id
            WHERE i.item_type = 'currency'
              AND bi.game_id = %(game_id)s;
        """

        params = {
            "game_id": game_id
        }

        await cursor.execute(query, params)

        return await cursor.fetchall()