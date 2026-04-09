from psycopg.rows import class_row

from ..base_repository import BaseRepository
from .get_all_unique_items import UniqueItem


async def get_unique_items_by_category(category: str) -> list[UniqueItem]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(UniqueItem)) as cursor:
        query = """
            SELECT ui.unique_item_id
                , ui.item_id
                , ic."label"
                , ic.api_id as category_api_id
                , ui."name"
                , ui."text"
                , ui.icon_url
                , it."value" as type
                , ui.item_metadata
                , ui.is_current
            FROM unique_item AS ui
            JOIN item AS i ON ui.item_id = i.item_id
            JOIN base_item AS bi ON i.base_item_id = bi.base_item_id
            JOIN item_type AS it ON bi.item_type_id = it.item_type_id
            JOIN item_category AS ic ON it.item_category_id = ic.item_category_id
            WHERE ic.api_id = %s
        """
        params = (category,)

        await cursor.execute(query, params)

        return await cursor.fetchall()
