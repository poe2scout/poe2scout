from psycopg.rows import class_row

from ..base_repository import BaseRepository
from .get_leagues import League


async def get_league_by_value(value: str) -> League | None:
    async with BaseRepository.get_db_cursor(row_factory=class_row(League)) as cursor:
        query = """
            SELECT "id", "value"
            FROM "League"
            WHERE "value" ILIKE %(value)s
        """

        params = {"value": value}

        await cursor.execute(query, params)

        return await cursor.fetchone()