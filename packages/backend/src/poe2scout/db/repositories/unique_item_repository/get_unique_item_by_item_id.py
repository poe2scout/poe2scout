from psycopg.rows import class_row

from .get_all_unique_items import UniqueItem
from ..base_repository import BaseRepository


async def get_unique_item_by_item_id(item_id: int, game_id: int) -> UniqueItem | None:
    async with BaseRepository.get_db_cursor(row_factory=class_row(UniqueItem)) as cursor:
        query = """
            SELECT ui.unique_item_id,
                ui.item_id,
                ui.icon_url,
                ui.text,
                ui.name,
                ui.item_metadata,
                ui.is_current,
                it.value AS type,
                ic.api_id AS category_api_id
            FROM unique_item AS ui
            JOIN item AS i ON ui.item_id = i.item_id
            JOIN base_item AS bi ON i.base_item_id = bi.base_item_id
            JOIN item_type AS it ON bi.item_type_id = it.item_type_id
            JOIN item_category AS ic ON ic.item_category_id = it.item_category_id
           WHERE ui.item_id = %(item_id)s
             AND bi.game_id = %(game_id)s
        """

        await cursor.execute(
            query,
            {
                "item_id": item_id,
                "game_id": game_id,
            },
        )

        return await cursor.fetchone()
