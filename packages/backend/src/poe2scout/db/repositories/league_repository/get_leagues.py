from psycopg.rows import class_row

from ..base_repository import BaseRepository, RepositoryModel


class League(RepositoryModel):
    league_id: int
    value: str


async def get_current_leagues(game_id: int) -> list[League]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(League)) as cursor:
        query = """
            SELECT league_id, value
             FROM league
            WHERE current_league = true
              AND game_id = %(game_id)s
        """

        params = {
            "game_id": game_id
        }

        await cursor.execute(query, params)

        return await cursor.fetchall()


async def get_leagues(game_id: int) -> list[League]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(League)) as cursor:
        query = """
            SELECT league_id, value
              FROM league
             WHERE game_id = %(game_id)s
        """

        params = {
            "game_id": game_id
        }
        await cursor.execute(query, params)

        return await cursor.fetchall()
