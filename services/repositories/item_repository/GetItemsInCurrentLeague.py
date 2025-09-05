from typing import Optional, List, Dict
from ..base_repository import BaseRepository
from pydantic import BaseModel
from datetime import datetime, timedelta
import time

class GetItemsInCurrentLeague(BaseRepository):
    async def execute(self, leagueId: int) -> List[int]:
        query = \
        """
            SELECT i."id"
              FROM "Item" as i
             WHERE EXISTS (
            SELECT 1
              FROM "PriceLog" as pl
             WHERE pl."itemId" = i."id"
               AND pl."leagueId" = %s
            );
        """
        result = (await self.execute_query(
            query, (leagueId,)))
        
        itemIds: List[int] = [item["id"] for item in result]
        
        return itemIds

