from psycopg.rows import dict_row

from ..base_repository import BaseRepository


async def is_item_a_currency(item_id: int) -> bool:
    async with BaseRepository.get_db_cursor(row_factory=dict_row) as cursor:
        query = """
            SELECT ci."id"
                , ci."itemId"
                , ci."apiId"
                , ci."text"
                , ci."iconUrl"
                , ci."currencyCategoryId"
                , cc."label"
                , cc."apiId" as "categoryApiId"
            FROM "CurrencyItem" as ci
            JOIN "CurrencyCategory" as cc on ci."currencyCategoryId" = cc."id"
            WHERE ci."itemId" = %s
        """

        await cursor.execute(query, (item_id,))

        return len(await cursor.fetchall()) == 1
