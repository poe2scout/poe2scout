from typing import Optional, List
from ..base_repository import BaseRepository
from pydantic import BaseModel

class League(BaseModel):
    id: int
    value: str

class GetLeagueByValue(BaseRepository):
    async def execute(self, value: str) -> League:
        if value == "Standard":
            value = "Rise of the Abyssal"
        if value == "Hardcore":
            value = "Rise of the Abyssal"
        league_query = """
            SELECT "id", "value" 
            FROM "League"
            WHERE "value" ILIKE %s
        """

        league = (await self.execute_query(
            league_query, (value,)))[0]

        return League(**league)