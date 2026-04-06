from psycopg.rows import class_row

from poe2scout.db.repositories.models import CurrencyItem

from ..base_repository import BaseRepository, RepositoryModel


class GetCurrencyItemIdModel(RepositoryModel):
    api_id: str


async def get_currency_item(api_id: str, game_id: int) -> CurrencyItem | None:
    async with BaseRepository.get_db_cursor(row_factory=class_row(CurrencyItem)) as cursor:
        query = """
            SELECT ci.currency_item_id,
                ci.item_id,
                ci.api_id,
                ci.text,
                ci.icon_url,
                ci.currency_category_id,
                cc.api_id as category_api_id
            FROM currency_item as ci
            JOIN currency_category as cc on ci.currency_category_id = cc.currency_category_id
            JOIN item AS i ON i.item_id = ci.item_id
            JOIN base_item AS bi ON bi.base_item_id = i.base_item_id
            WHERE ci.api_id = %(api_id)s
              AND bi.game_id = %(game_id)s
        """

        params = {
            "api_id": api_id,
            "game_id": game_id
        }

        await cursor.execute(query, params)

        return await cursor.fetchone()

async def get_divine_item(game_id: int) -> CurrencyItem:
    divine_item = await get_currency_item("divine", game_id)
    assert divine_item is not None
    return divine_item
    
async def get_chaos_item(game_id: int) -> CurrencyItem:
    chaos_item = await get_currency_item("chaos", game_id)
    assert chaos_item is not None
    return chaos_item

async def get_exalted_item(game_id: int) -> CurrencyItem:
    exalted_item = await get_currency_item("exalted", game_id)
    assert exalted_item is not None
    return exalted_item
