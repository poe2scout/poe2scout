from ..base_repository import BaseRepository


async def update_currency_icon_url(icon_url: str, id: int):
    async with BaseRepository.get_db_cursor() as cursor:
        query = """
            UPDATE "CurrencyItem"
            SET "iconUrl" = %(icon_url)s
            WHERE "id" = %(id)s
        """

        await cursor.execute(query, params={"icon_url": icon_url, "id": id})