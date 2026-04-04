from ..base_repository import BaseRepository


async def update_base_item_icon_url(icon_url: str, base_item_id: int):
    async with BaseRepository.get_db_cursor() as cursor:
        query = """
            UPDATE base_item
            SET icon_url = %(icon_url)s
            WHERE base_item_id = %(base_item_id)s
        """

        await cursor.execute(query, params={"icon_url": icon_url, "base_item_id": base_item_id})
