from psycopg.rows import class_row

from ..base_repository import BaseRepository, RepositoryModel


class League(RepositoryModel):
    league_id: int
    value: str


async def get_leagues() -> list[League]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(League)) as cursor:
        query = """
            SELECT league_id, value
            FROM league
            WHERE current_league = true
        """
        await cursor.execute(query)

        return await cursor.fetchall()


async def get_all_leagues() -> list[League]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(League)) as cursor:
        query = """
            SELECT league_id, value
            FROM league
        """
        await cursor.execute(query)

        return await cursor.fetchall()
