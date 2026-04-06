from psycopg.rows import class_row

from ..base_repository import BaseRepository
from .get_leagues import League


async def get_league_by_value(value: str, game_id: int) -> League | None:
    async with BaseRepository.get_db_cursor(row_factory=class_row(League)) as cursor:
        query = """
            SELECT l.league_id,
                   l.value,
                   l.base_currency_item_id,
                   ci.api_id AS base_currency_api_id,
                   ci.text AS base_currency_text
              FROM league AS l
              JOIN currency_item AS ci
                ON ci.item_id = l.base_currency_item_id
             WHERE l.value ILIKE %(value)s
               AND l.game_id = %(game_id)s
        """

        params = {
            "value": value,
            "game_id": game_id
        }

        await cursor.execute(query, params)

        return await cursor.fetchone()
