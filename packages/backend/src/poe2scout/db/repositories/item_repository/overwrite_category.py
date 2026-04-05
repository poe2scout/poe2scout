from ..base_repository import BaseRepository


async def overwrite_category(category_id: int, new_category_id: int):
    async with BaseRepository.get_db_cursor() as cursor:
        query = """
            UPDATE item_type as it
            SET item_category_id = %(new_category_id)s
            Where item_category_id = %(category_id)s
        """

        await cursor.execute(
            query, {"category_id": category_id, "new_category_id": new_category_id}
        )
