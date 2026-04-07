from datetime import datetime

from ..base_repository import BaseRepository


async def get_currency_fetch_status(start_time: datetime) -> bool:
    async with BaseRepository.get_db_cursor() as cursor:
        query = """
            SELECT 1
              FROM currency_item AS ci
              JOIN price_log AS pl ON ci.item_id = pl.item_id
             WHERE pl.created_at >= %(start_time)s
             LIMIT 1
        """

        params = {
            "start_time": start_time,
        }

        await cursor.execute(query, params)

        return cursor.rowcount != 0


class GetCurrencyFetchStatus(BaseRepository):
    async def execute(self, start_time: datetime) -> bool:
        return await get_currency_fetch_status(start_time)
