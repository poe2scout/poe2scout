from psycopg.rows import class_row
from pydantic import Field

from ..base_repository import BaseRepository, RepositoryModel


class ItemCategory(RepositoryModel):
    id: int
    api_id: str = Field(alias="apiId")
    label: str


async def get_all_item_categories() -> list[ItemCategory]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(ItemCategory)) as cursor:
        query = """
            SELECT "id", "apiId", "label" FROM "ItemCategory"
        """

        await cursor.execute(query)

        return await cursor.fetchall()


class GetAllItemCategories(BaseRepository):
    async def execute(self) -> list[ItemCategory]:
        return await get_all_item_categories()
