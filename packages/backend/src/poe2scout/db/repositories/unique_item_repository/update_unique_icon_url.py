from ..base_repository import BaseRepository


async def update_unique_icon_url(icon_url: str, unique_item_id: int):
    async with BaseRepository.get_db_cursor() as cursor:
        query = """
            UPDATE unique_item
            SET icon_url = %(icon_url)s
            WHERE unique_item_id = %(unique_item_id)s
        """

        await cursor.execute(
            query,
            params={"icon_url": icon_url, "unique_item_id": unique_item_id},
        )
