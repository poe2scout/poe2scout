from typing import Optional, Awaitable
from ..base_repository import BaseRepository
from pydantic import BaseModel


class GetItemPriceModel(BaseModel):
    itemId: int
    leagueId: int

class GetItemPrice(BaseRepository):
    async def execute(self, itemId: int, leagueId: int) -> float:
        item_query = """
            SELECT "price" FROM "PriceLog"
            WHERE "itemId" = %s AND "leagueId" = %s
            ORDER BY "createdAt" DESC
            LIMIT 1
        """

        price = await self.execute_query(
            item_query, (itemId, leagueId))
        
        if len(price) == 0:
            return 0 # Default div price in exalts. This method is / should only be called to get divine price or chaos price.
        else:
            return price[0]["price"]
