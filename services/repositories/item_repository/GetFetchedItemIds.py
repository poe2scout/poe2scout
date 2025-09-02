from typing import Optional, Awaitable
from ..base_repository import BaseRepository
from pydantic import BaseModel
from .GetAllCurrencyItems import CurrencyItem
from datetime import datetime, timedelta


class GetFetchedItemIds(BaseRepository):
    async def execute(self, currentHour: str, leagueId: int) -> list[int]:
        currentHour = int(currentHour)
        ranges = [[0, 12], [12, 24]]

        for range in ranges:
            if currentHour >= range[0] and currentHour < range[1]:
                currentStart = range[0]
                currentEnd = range[1]
        currentStart = datetime.now().replace(hour=currentStart, minute=0, second=0, microsecond=0)
        currentDay = datetime.now().day
        if currentEnd == 24:
            currentEnd = 0
            currentDay = (datetime.now() + timedelta(days=1)).day
        currentEnd = datetime.now().replace(day=currentDay, hour=currentEnd, minute=0, second=0, microsecond=0)

        item_query = """
            SELECT DISTINCT i."id" FROM "Item" as i
            JOIN "PriceLog" as pl ON i."id" = pl."itemId"
            JOIN "League" as l ON pl."leagueId" = l."id"
            WHERE pl."createdAt" > %s AND pl."createdAt" < %s AND l."id" = %s
        """
        itemIds = (await self.execute_query(
            item_query, (currentStart, currentEnd, leagueId)))
    

        return [itemId['id'] for itemId in itemIds]
