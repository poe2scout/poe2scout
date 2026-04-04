from ..base_repository import BaseRepository, RepositoryModel, scalar_as


class RecordPriceModel(RepositoryModel):
    item_id: int
    league_id: int
    price: float
    quantity: int


async def record_price(price: RecordPriceModel) -> int:
    async with BaseRepository.get_db_cursor(row_factory=scalar_as(int)) as cursor:
        query = """
            INSERT INTO "PriceLog" ("itemId", "leagueId", "price", "quantity", "createdAt")
            VALUES (%(itemId)s, %(leagueId)s, %(price)s, %(quantity)s, NOW())
            RETURNING "id"
        """

        await cursor.execute(query, price.model_dump(by_alias=True))

        return await anext(cursor)


async def record_price_bulk(prices: list[RecordPriceModel], epoch: int):
    async with BaseRepository.get_db_cursor() as cursor:
        query = """
INSERT INTO "PriceLog" ("itemId", "leagueId", "price", "quantity", "createdAt")
VALUES (%(itemId)s, %(leagueId)s, %(price)s, %(quantity)s, to_timestamp(%(createdAt)s))
        """
        price_dict_list = [
            {**price.model_dump(by_alias=True), "createdAt": epoch} for price in prices
        ]

        await cursor.executemany(query, price_dict_list)
