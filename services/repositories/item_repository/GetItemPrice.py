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

        price = (await self.execute_query(
            item_query, (itemId, leagueId)))[0]["price"]

        return price
