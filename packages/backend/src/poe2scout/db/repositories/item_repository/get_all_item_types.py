from psycopg.rows import class_row
from pydantic import Field

from ..base_repository import BaseRepository, RepositoryModel


class ItemType(RepositoryModel):
    id: int
    value: str
    category_id: int = Field(alias="categoryId")


async def get_all_item_types() -> list[ItemType]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(ItemType)) as cursor:
        query = """
            SELECT "id", "value", "categoryId" FROM "ItemType"
        """

        await cursor.execute(query)

        return await cursor.fetchall()


class GetAllItemTypes(BaseRepository):
    async def execute(self) -> list[ItemType]:
        return await get_all_item_types()
