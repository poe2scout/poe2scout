from typing import Optional

from psycopg.rows import class_row

from ..base_repository import BaseRepository, RepositoryModel


class BaseItem(RepositoryModel):
    id: int
    type_id: int
    icon_url: Optional[str] = None
    item_metadata: Optional[dict] = None


async def get_all_base_items() -> list[BaseItem]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(BaseItem)) as cursor:
        query = """
            SELECT "bi"."id"
                , "bi"."typeId"
                , "bi"."iconUrl"
                , "bi"."itemMetadata"
            FROM "BaseItem" as bi
        """

        await cursor.execute(query)

        return await cursor.fetchall()


class GetAllBaseItems(BaseRepository):
    async def execute(self) -> list[BaseItem]:
        return await get_all_base_items()
