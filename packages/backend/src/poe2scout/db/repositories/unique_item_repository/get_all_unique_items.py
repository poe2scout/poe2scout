from typing import Optional

from psycopg.rows import class_row

from ..base_repository import BaseRepository, RepositoryModel


class UniqueItem(RepositoryModel):
    unique_item_id: int
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
            SELECT ui.unique_item_id,
                ui.item_id,
                ui.icon_url,
                ui.text,
                ui.name,
                ui.item_metadata,
                it.value as type,
                ic.api_id as category_api_id
            FROM unique_item as ui
            JOIN item AS i ON ui.item_id = i.item_id
            JOIN base_item AS bi ON i.base_item_id = bi.base_item_id
            JOIN item_type AS it ON bi.item_type_id = it.item_type_id
            JOIN item_category AS ic on ic.item_category_id = it.item_category_id
        """

        await cursor.execute(query)

        return await cursor.fetchall()


class GetAllUniqueItems(BaseRepository):
    async def execute(self) -> list[UniqueItem]:
        return await get_all_unique_items()
