from ..base_repository import BaseRepository


async def set_unique_item_current(unique_item_id: int, is_current: bool) -> None:
    async with BaseRepository.get_db_cursor() as cursor:
        query = """
            UPDATE unique_item
            SET is_current = %(is_current)s
            WHERE unique_item_id = %(unique_item_id)s
        """

        await cursor.execute(
            query,
            params={
                "unique_item_id": unique_item_id,
                "is_current": is_current,
            },
        )
