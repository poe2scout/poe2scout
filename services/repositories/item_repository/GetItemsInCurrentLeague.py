from typing import Optional, List, Dict
from ..base_repository import BaseRepository
from pydantic import BaseModel
from datetime import datetime, timedelta
import time

class GetItemsInCurrentLeague(BaseRepository):
    async def execute(self, leagueId: int) -> List[int]:
        query = \
        """
            SELECT DISTINCT i."id"
            FROM "Item" as i
            JOIN "PriceLog" as pl ON i."id" = pl."itemId"
            JOIN "League" as l ON pl."leagueId" = l."id"
            WHERE l."id" = %s
        """
        result = (await self.execute_query(
            query, (leagueId,)))
        
        itemIds: List[int] = [item["id"] for item in result]
        
        return itemIds

