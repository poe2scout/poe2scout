from typing import Optional, Awaitable
from ..base_repository import BaseRepository
from pydantic import BaseModel


class RecordPriceModel(BaseModel):
    itemId: int
    leagueId: int
    price: float
    quantity: int

class RecordPrice(BaseRepository):
    async def execute(self, price: RecordPriceModel) -> Awaitable[int]:
        item_query = """
            INSERT INTO "PriceLog" ("itemId", "leagueId", "price", "quantity", "createdAt")
            VALUES (%(itemId)s, %(leagueId)s, %(price)s, %(quantity)s, NOW())
            RETURNING "id"
        """

        priceLogId = await self.execute_single(
            item_query, price.model_dump())

        return priceLogId
