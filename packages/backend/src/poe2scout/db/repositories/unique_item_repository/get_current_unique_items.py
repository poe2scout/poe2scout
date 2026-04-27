from psycopg.rows import class_row

from ..base_repository import BaseRepository
from .get_all_unique_items import UniqueItem


async def get_current_unique_items(game_id: int) -> list[UniqueItem]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(UniqueItem)) as cursor:
        query = """
            SELECT 
                ui.unique_item_id,
                ui.item_id,
                ui.icon_url,
                ui.text,
                ui.name,
                ui.item_metadata,
                ui.is_current,
                it.value as type,
                ic.api_id as category_api_id
            FROM unique_item as ui
            JOIN item AS i ON ui.item_id = i.item_id
            JOIN base_item AS bi ON i.base_item_id = bi.base_item_id
            JOIN item_type AS it ON bi.item_type_id = it.item_type_id
            JOIN item_category AS ic on ic.item_category_id = it.item_category_id
            WHERE bi.game_id = %(game_id)s
              AND ui.is_current = TRUE
        """

        await cursor.execute(query, {"game_id": game_id})
        return await cursor.fetchall()
