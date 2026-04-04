from ..base_repository import BaseRepository


async def update_unique_icon_url(icon_url: str, id: int):
    async with BaseRepository.get_db_cursor() as cursor:
        query = """
            UPDATE "UniqueItem"
            SET "iconUrl" = %(icon_url)s
            WHERE "id" = %(id)s
        """

        await cursor.execute(query, params={"icon_url": icon_url, "id": id})