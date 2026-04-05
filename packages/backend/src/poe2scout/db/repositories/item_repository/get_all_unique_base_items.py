from typing import Optional

from psycopg.rows import class_row

from ..base_repository import BaseRepository, RepositoryModel


class UniqueBaseItem(RepositoryModel):
    base_item_id: int
    icon_url: Optional[str] = None
    item_metadata: Optional[dict] = None
    item_id: int
    name: str
    api_id: str


async def get_all_unique_base_items() -> list[UniqueBaseItem]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(UniqueBaseItem)) as cursor:
        query = """
                        WITH unique_ids AS (
                            SELECT DISTINCT base_item_id FROM item
                            WHERE item_type = 'unique'
                        ),
                        valid_items AS (
                            SELECT * FROM item
                            WHERE item_type = 'base'
                        )
                        SELECT
                            bi.base_item_id,
                            bi.icon_url,
                            bi.item_metadata,
                            i.item_id as item_id,
                            it.value as name,
                            ic.api_id
                        FROM base_item as bi
                        JOIN valid_items as i ON bi.base_item_id = i.base_item_id
                        JOIN item_type as it ON bi.item_type_id = it.item_type_id
                        JOIN item_category as ic on it.item_category_id = ic.item_category_id
                        WHERE bi.base_item_id IN (SELECT base_item_id FROM unique_ids)
        """

        await cursor.execute(query)

        return await cursor.fetchall()


class GetAllUniqueBaseItems(BaseRepository):
    async def execute(self) -> list[UniqueBaseItem]:
        return await get_all_unique_base_items()
