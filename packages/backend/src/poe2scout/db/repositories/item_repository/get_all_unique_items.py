from typing import Optional

from psycopg.rows import class_row

from ..base_repository import BaseRepository, RepositoryModel


class UniqueItem(RepositoryModel):
    id: int
    item_id: int
    icon_url: Optional[str] = None
    text: str
    name: str
    category_api_id: str
    item_metadata: Optional[dict] = None
    type: str
    is_chanceable: Optional[bool] = False


async def get_all_unique_items() -> list[UniqueItem]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(UniqueItem)) as cursor:
        query = """
            SELECT ui."id",
                ui."itemId",
                ui."iconUrl",
                ui."text",
                ui."name",
                ui."itemMetadata",
                it."value" as "type",
                ic."apiId" as "categoryApiId"
            FROM "UniqueItem" as ui
            JOIN "Item" AS i ON ui."itemId" = i."id"
            JOIN "BaseItem" AS bi ON i."baseItemId" = bi."id"
            JOIN "ItemType" AS it ON bi."typeId" = it."id"
            JOIN "ItemCategory" AS ic on ic."id" = it."categoryId"
        """

        await cursor.execute(query)

        return await cursor.fetchall()


class GetAllUniqueItems(BaseRepository):
    async def execute(self) -> list[UniqueItem]:
        return await get_all_unique_items()
