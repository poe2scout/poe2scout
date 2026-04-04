from psycopg.rows import class_row

from ..base_repository import BaseRepository, RepositoryModel


class League(RepositoryModel):
    id: int
    value: str


async def get_leagues() -> list[League]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(League)) as cursor:
        query = """
            SELECT "id", "value"
            FROM "League"
            WHERE "currentLeague" = true
        """
        await cursor.execute(query)

        return await cursor.fetchall()


async def get_all_leagues() -> list[League]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(League)) as cursor:
        query = """
            SELECT "id", "value"
            FROM "League"
        """
        await cursor.execute(query)

        return await cursor.fetchall()
