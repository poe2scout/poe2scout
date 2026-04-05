from ..base_repository import BaseRepository


async def update_currency_icon_url(icon_url: str, currency_item_id: int):
    async with BaseRepository.get_db_cursor() as cursor:
        query = """
            UPDATE currency_item
            SET icon_url = %(icon_url)s
            WHERE currency_item_id = %(currency_item_id)s
        """

        await cursor.execute(
            query,
            params={"icon_url": icon_url, "currency_item_id": currency_item_id},
        )
