from psycopg.rows import class_row

from poe2scout.db.repositories.models import CurrencyItem

from ..base_repository import BaseRepository


async def get_all_currency_items(game_id: int) -> list[CurrencyItem]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(CurrencyItem)) as cursor:
        query = """
            SELECT ci.currency_item_id
                 , ci.item_id
                 , ci.currency_category_id
                 , cc.api_id as category_api_id
                 , ci.api_id, ci.text
                 , ci.icon_url
                 , ci.item_metadata
              FROM currency_item as ci
              JOIN currency_category as cc on ci.currency_category_id = cc.currency_category_id
              JOIN item as i ON ci.item_id = i.item_id
              JOIN base_item as bi ON bi.base_item_id = i.base_item_id
             WHERE bi.game_id = %(game_id)s
        """

        params = {
            "game_id": game_id
        }

        await cursor.execute(query, params)

        return await cursor.fetchall()

