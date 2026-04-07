from psycopg.rows import class_row

from ..base_repository import BaseRepository, RepositoryModel


class ItemCategory(RepositoryModel):
    item_category_id: int
    api_id: str
    label: str


async def get_all_item_categories() -> list[ItemCategory]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(ItemCategory)) as cursor:
        query = """
            SELECT item_category_id, api_id, label
              FROM item_category
             WHERE category_kind = 'item'
        """

        await cursor.execute(query)

        return await cursor.fetchall()
