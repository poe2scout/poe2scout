from psycopg.rows import class_row

from poe2scout.db.repositories.models import CurrencyItem

from ..base_repository import BaseRepository


async def get_all_currency_items() -> list[CurrencyItem]:
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
        """

        await cursor.execute(query)

        return await cursor.fetchall()


class GetAllCurrencyItems(BaseRepository):
    async def execute(self) -> list[CurrencyItem]:
        return await get_all_currency_items()
