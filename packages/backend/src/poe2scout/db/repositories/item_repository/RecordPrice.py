from typing import List

from ..base_repository import BaseRepository, scalar_as
from pydantic import BaseModel


class RecordPriceModel(BaseModel):
    itemId: int
    leagueId: int
    price: float
    quantity: int


class RecordPrice(BaseRepository):
    async def execute(self, price: RecordPriceModel) -> int:
        async with self.get_db_cursor(
            rowFactory=scalar_as(int)
        ) as cursor:
            query = """
                INSERT INTO "PriceLog" ("itemId", "leagueId", "price", "quantity", "createdAt")
                VALUES (%(itemId)s, %(leagueId)s, %(price)s, %(quantity)s, NOW())
                RETURNING "id"
            """

            await cursor.execute(query, price.model_dump())

            return await anext(cursor)


class RecordPriceBulk(BaseRepository):
    async def execute(self, prices: List[RecordPriceModel], epoch: int):
        async with self.get_db_cursor() as cursor:
            query = """
INSERT INTO "PriceLog" ("itemId", "leagueId", "price", "quantity", "createdAt")
VALUES (%(itemId)s, %(leagueId)s, %(price)s, %(quantity)s, to_timestamp(%(createdAt)s))
            """
            # Add the timestamp to each price dictionary
            priceDictList = [{**price.model_dump(), "createdAt": epoch} for price in prices]

            await cursor.executemany(query, priceDictList)
