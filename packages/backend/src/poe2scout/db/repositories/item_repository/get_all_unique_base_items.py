from typing import Optional

from psycopg.rows import class_row

from ..base_repository import BaseRepository, RepositoryModel


class UniqueBaseItem(RepositoryModel):
    id: int
    icon_url: Optional[str] = None
    item_metadata: Optional[dict] = None
    item_id: int
    name: str
    api_id: str


async def get_all_unique_base_items() -> list[UniqueBaseItem]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(UniqueBaseItem)) as cursor:
        query = """
                        WITH unique_ids AS (
                            SELECT DISTINCT "baseItemId" FROM "Item"
                            WHERE "itemType" = 'unique'
                        ),
                        valid_items AS (
                            SELECT * FROM "Item"
                            WHERE "itemType" = 'base'
                        )
                        SELECT
                            "bi"."id",
                            "bi"."iconUrl",
                            "bi"."itemMetadata",
                            "i".id as "itemId",
                            "it"."value" as name,
                            ic."apiId"
                        FROM "BaseItem" as bi
                        JOIN valid_items as i ON "bi"."id" = "i"."baseItemId"
                        JOIN "ItemType" as it ON "bi"."typeId" = "it"."id"
                        JOIN "ItemCategory" as ic on it."categoryId" = ic.id
                        WHERE "bi"."id" IN (SELECT "baseItemId" FROM unique_ids)
        """

        await cursor.execute(query)

        return await cursor.fetchall()


class GetAllUniqueBaseItems(BaseRepository):
    async def execute(self) -> list[UniqueBaseItem]:
        return await get_all_unique_base_items()
