from typing import List, Optional, Awaitable
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


class RecordPriceBulk(BaseRepository):
    async def execute(self, prices: List[RecordPriceModel], epoch: int):
        item_query = """
            INSERT INTO "PriceLog" ("itemId", "leagueId", "price", "quantity", "createdAt")
            VALUES (%(itemId)s, %(leagueId)s, %(price)s, %(quantity)s, to_timestamp(%(createdAt)s))
        """
        # Add the timestamp to each price dictionary
        priceDictList = [{**price.model_dump(), 'createdAt': epoch} for price in prices]

        await self.execute_many(item_query, priceDictList)
