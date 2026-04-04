from psycopg.rows import class_row

from ..base_repository import BaseRepository, RepositoryModel


class Item(RepositoryModel):
    id: int
    base_item_id: int
    item_type: str


async def get_all_items() -> list[Item]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(Item)) as cursor:
        query = """
            SELECT "id", "baseItemId", "itemType"
            FROM "Item"
        """

        await cursor.execute(query)

        return await cursor.fetchall()


class GetAllItems(BaseRepository):
    async def execute(self) -> list[Item]:
        return await get_all_items()
