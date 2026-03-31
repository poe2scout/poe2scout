from ..base_repository import BaseRepository


class UpdatePairHistories(BaseRepository):
    async def execute(self):
        async with self.get_db_cursor() as cursor:
            query = """
SELECT update_currency_history_incrementally();
            """

            await cursor.execute(query)

            return
