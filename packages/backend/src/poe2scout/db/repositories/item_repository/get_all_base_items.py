from typing import Optional

from psycopg.rows import class_row

from ..base_repository import BaseRepository, RepositoryModel


class BaseItem(RepositoryModel):
    base_item_id: int
    item_type_id: int
    icon_url: Optional[str] = None
    item_metadata: Optional[dict] = None


async def get_all_base_items() -> list[BaseItem]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(BaseItem)) as cursor:
        query = """
            SELECT bi.base_item_id
                , bi.item_type_id
                , bi.icon_url
                , bi.item_metadata
            FROM base_item as bi
        """

        await cursor.execute(query)

        return await cursor.fetchall()


class GetAllBaseItems(BaseRepository):
    async def execute(self) -> list[BaseItem]:
        return await get_all_base_items()
