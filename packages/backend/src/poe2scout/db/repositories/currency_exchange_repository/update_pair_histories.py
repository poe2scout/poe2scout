from ..base_repository import BaseRepository


async def update_pair_histories():
    async with BaseRepository.get_db_cursor() as cursor:
        query = """
SELECT update_currency_history_incrementally();
        """

        await cursor.execute(query)