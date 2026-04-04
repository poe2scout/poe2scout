from psycopg.rows import class_row

from ..base_repository import BaseRepository
from .get_all_unique_items import UniqueItem


async def get_unique_items_by_category(category: str) -> list[UniqueItem]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(UniqueItem)) as cursor:
        query = """
            SELECT ui."id"
                , ui."itemId"
                , ic."label"
                , ic."apiId" as "categoryApiId"
                , ui."name"
                , ui."text"
                , ui."iconUrl"
                , it."value" as type
                , ui."itemMetadata"
            FROM "UniqueItem" AS ui
            JOIN "Item" AS i ON ui."itemId" = i."id"
            JOIN "BaseItem" AS bi ON i."baseItemId" = bi."id"
            JOIN "ItemType" AS it ON bi."typeId" = it."id"
            JOIN "ItemCategory" AS ic ON it."categoryId" = ic."id"
            WHERE ic."apiId" = %s
        """
        params = (category,)

        await cursor.execute(query, params)

        return await cursor.fetchall()

