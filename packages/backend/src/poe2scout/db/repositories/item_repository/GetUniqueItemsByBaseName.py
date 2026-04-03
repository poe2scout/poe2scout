from typing import List

from psycopg.rows import class_row
from ..base_repository import BaseRepository
from .GetAllUniqueItems import UniqueItem


class GetUniqueItemsByBaseName(BaseRepository):
    async def execute(self, baseName: str) -> List[UniqueItem]:
        async with self.get_db_cursor(
            rowFactory=class_row(UniqueItem)
        ) as cursor:

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
            await cursor.execute(query, (baseName,))

            return await cursor.fetchall()
