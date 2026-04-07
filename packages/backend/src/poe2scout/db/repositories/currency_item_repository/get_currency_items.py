from psycopg.rows import class_row

from poe2scout.db.repositories.models import CurrencyItem

from ..base_repository import BaseRepository


async def get_currency_items(
    api_ids: list[str],
    game_id: int
) -> list[CurrencyItem]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(CurrencyItem)) as cursor:
        query = """
SELECT ci.currency_item_id
    , ci.item_id
    , ci.api_id
    , ci.text
    , ci.icon_url
    , ci.item_category_id AS currency_category_id
    , cc.api_id AS category_api_id
FROM currency_item AS ci
JOIN item_category AS cc ON ci.item_category_id = cc.item_category_id
JOIN item AS i ON ci.item_id = i.item_id
JOIN base_item AS bi ON i.base_item_id = bi.base_item_id
WHERE ci.api_id = ANY(%(api_ids)s)
  AND bi.game_id = %(game_id)s
        """

        params = {
            "api_ids": api_ids,
            "game_id": game_id
        }

        await cursor.execute(query, params)

        return await cursor.fetchall()
