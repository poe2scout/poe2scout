from psycopg.rows import class_row

from ..base_repository import BaseRepository
from .get_leagues import League


async def get_league_by_value(value: str, game_id: int) -> League | None:
    async with BaseRepository.get_db_cursor(row_factory=class_row(League)) as cursor:
        query = """
            SELECT league_id
                 , value
              FROM league
             WHERE value ILIKE %(value)s
               AND game_id = %(game_id)s
        """

        params = {
            "value": value,
            "game_id": game_id
        }

        await cursor.execute(query, params)

        return await cursor.fetchone()
