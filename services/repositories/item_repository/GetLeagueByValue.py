from typing import Optional, List
from ..base_repository import BaseRepository
from pydantic import BaseModel

class League(BaseModel):
    id: int
    value: str

class GetLeagueByValue(BaseRepository):
    async def execute(self, value: str) -> League:
        if value == "Standard":
            value = "Dawn of the Hunt"
        if value == "Hardcore":
            value = "HC Dawn of the Hunt"
        league_query = """
            SELECT "id", "value" 
            FROM "League"
            WHERE "value" ILIKE %s
        """

        league = (await self.execute_query(
            league_query, (value,)))[0]

        return League(**league)