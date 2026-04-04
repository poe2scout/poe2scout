from psycopg.rows import class_row

from poe2scout.db.repositories.models import CurrencyItem

from ..base_repository import BaseRepository


async def get_currency_items(api_ids: list[str]) -> list[CurrencyItem]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(CurrencyItem)) as cursor:
        query = """
SELECT ci.currency_item_id
    , ci.item_id
    , ci.api_id
    , ci.text
    , ci.icon_url
    , ci.currency_category_id
    , cc.api_id AS category_api_id
FROM currency_item AS ci
JOIN currency_category AS cc ON ci.currency_category_id = cc.currency_category_id
WHERE ci.api_id = ANY(%s)
        """

        await cursor.execute(query, (api_ids,))

        return await cursor.fetchall()
