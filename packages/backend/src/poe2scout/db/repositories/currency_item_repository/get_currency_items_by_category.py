from psycopg.rows import class_row

from poe2scout.db.repositories.models import CurrencyItem

from ..base_repository import BaseRepository


async def get_currency_items_by_category(category: str) -> list[CurrencyItem]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(CurrencyItem)) as cursor:
        query = """
            SELECT ci.currency_item_id
                , ci.item_id
                , cc.api_id as category_api_id
                , ci.api_id, ci.text
                , ci.icon_url
                , ci.currency_category_id
                , ci.item_metadata
            FROM currency_item AS ci
            JOIN currency_category AS cc ON ci.currency_category_id = cc.currency_category_id
            WHERE cc.api_id ILIKE %s
        """
        params = (category,)

        await cursor.execute(query, params)

        return await cursor.fetchall()
