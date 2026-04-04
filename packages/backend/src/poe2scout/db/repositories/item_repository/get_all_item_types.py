from psycopg.rows import class_row

from ..base_repository import BaseRepository, RepositoryModel


class ItemType(RepositoryModel):
    item_type_id: int
    value: str
    item_category_id: int


async def get_all_item_types() -> list[ItemType]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(ItemType)) as cursor:
        query = """
            SELECT item_type_id, value, item_category_id FROM item_type
        """

        await cursor.execute(query)

        return await cursor.fetchall()


class GetAllItemTypes(BaseRepository):
    async def execute(self) -> list[ItemType]:
        return await get_all_item_types()
