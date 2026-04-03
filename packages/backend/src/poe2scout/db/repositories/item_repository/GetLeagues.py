from typing import List

from psycopg.rows import class_row
from ..base_repository import BaseRepository
from pydantic import BaseModel


class League(BaseModel):
    id: int
    value: str


class GetLeagues(BaseRepository):
    async def execute(self) -> list[League]:
        async with self.get_db_cursor(
            rowFactory=class_row(League)
        ) as cursor:
            query = """
                SELECT "id", "value" 
                FROM "League"
                WHERE "currentLeague" = true
            """
            await cursor.execute(query)

            return await cursor.fetchall()


class GetAllLeagues(BaseRepository):
    async def execute(self) -> List[League]:
        async with self.get_db_cursor(
            rowFactory=class_row(League)
        ) as cursor:
            query = """
                SELECT "id", "value" 
                FROM "League"
            """
            await cursor.execute(query)

            return await cursor.fetchall()
