from psycopg.rows import class_row

from ..base_repository import BaseRepository
from .get_all_unique_items import UniqueItem


async def get_unique_items_by_base_name(base_name: str) -> list[UniqueItem]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(UniqueItem)) as cursor:
        query = """
            SELECT ui."id"
                , ui."itemId"
                , ui."name"
                , ui."text"
                , ic."apiId" as "categoryApiId"
                , ui."iconUrl"
                , it."value" as type
                , ui."itemMetadata"
                , ui."isChanceable"
            FROM "UniqueItem" AS ui
            JOIN "Item" AS i ON ui."itemId" = i."id"
            JOIN "BaseItem" AS bi ON i."baseItemId" = bi."id"
            JOIN "ItemType" AS it ON bi."typeId" = it."id"
            JOIN "ItemCategory" AS ic ON it."categoryId" = ic."id"
            WHERE it."value" = %s
        """
        await cursor.execute(query, (base_name,))

        return await cursor.fetchall()
