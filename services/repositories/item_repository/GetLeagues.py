from typing import Optional, List
from ..base_repository import BaseRepository
from pydantic import BaseModel

class League(BaseModel):
    id: int
    value: str

class GetLeagues(BaseRepository):
    async def execute(self) -> List[League]:
        league_query = """
            SELECT "id", "value" 
            FROM "League"
            WHERE "currentLeague" = true
        """
        leagues = await self.execute_query(
            league_query)

        return [League(**league) for league in leagues]
    
class GetAllLeagues(BaseRepository):
    async def execute(self) -> List[League]:
        league_query = """
            SELECT "id", "value" 
            FROM "League"
        """
        leagues = await self.execute_query(
            league_query)

        return [League(**league) for league in leagues]