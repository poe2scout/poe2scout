from psycopg.rows import class_row

from poe2scout.db.repositories.models import CurrencyItem

from ..base_repository import BaseRepository


async def get_currency_item_by_item_id(item_id: int, game_id: int) -> CurrencyItem | None:
    async with BaseRepository.get_db_cursor(row_factory=class_row(CurrencyItem)) as cursor:
        query = """
            SELECT ci.currency_item_id,
                ci.item_id,
                ci.api_id,
                ci.text,
                ci.icon_url,
                ci.item_metadata,
                ci.item_category_id AS currency_category_id,
                cc.api_id AS category_api_id
            FROM currency_item AS ci
            JOIN item_category AS cc ON ci.item_category_id = cc.item_category_id
            JOIN item AS i ON i.item_id = ci.item_id
            JOIN base_item AS bi ON bi.base_item_id = i.base_item_id
           WHERE ci.item_id = %(item_id)s
             AND bi.game_id = %(game_id)s
        """

        await cursor.execute(
            query,
            {
                "item_id": item_id,
                "game_id": game_id,
            },
        )

        return await cursor.fetchone()
