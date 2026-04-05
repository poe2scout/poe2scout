from psycopg.rows import dict_row

from ..base_repository import BaseRepository


async def is_item_a_currency(item_id: int) -> bool:
    async with BaseRepository.get_db_cursor(row_factory=dict_row) as cursor:
        query = """
            SELECT 1
            FROM currency_item as ci
            WHERE ci.item_id = %s
        """

        await cursor.execute(query, (item_id,))

        return len(await cursor.fetchall()) == 1
