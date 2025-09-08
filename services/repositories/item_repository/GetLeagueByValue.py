from typing import Optional, List
from ..base_repository import BaseRepository
from pydantic import BaseModel
from psycopg.rows import class_row

class League(BaseModel):
    id: int
    value: str

class GetLeagueByValue(BaseRepository):
    async def execute(self, value: str) -> League | None:
        async with self.get_db_cursor(rowFactory=class_row(League)) as cursor:
            query = """
                SELECT "id", "value" 
                FROM "League"
                WHERE "value" ILIKE %(value)s
            """

            params = {
                "value": value
            }

            await cursor.execute(query, params)

            league = await cursor.fetchone()


            return league