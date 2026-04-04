from ..base_repository import BaseRepository, scalar_as


async def get_unique_item_id(name: str) -> int | None:
    async with BaseRepository.get_db_cursor(row_factory=scalar_as(int)) as cursor:
        query = """
            SELECT "itemId" FROM "UniqueItem"
            WHERE "name" = %s
        """

        await cursor.execute(query, (name,))

        return await cursor.fetchone()
