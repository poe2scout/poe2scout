from ..base_repository import BaseRepository, RepositoryModel, scalar_as


class RecordPriceModel(RepositoryModel):
    item_id: int
    league_id: int
    price: float
    quantity: int
    realm_id: int


async def record_price(price: RecordPriceModel) -> int:
    async with BaseRepository.get_db_cursor(row_factory=scalar_as(int)) as cursor:
        query = """
            INSERT INTO price_log (item_id, league_id, realm_id, price, quantity, created_at)
            VALUES (%(item_id)s, %(league_id)s, %(realm_id)s, %(price)s, %(quantity)s, NOW())
            RETURNING price_log_id
        """

        await cursor.execute(query, price.model_dump())

        return await anext(cursor)


async def record_price_bulk(prices: list[RecordPriceModel], epoch: int):
    async with BaseRepository.get_db_cursor() as cursor:
        query = """
INSERT INTO price_log (item_id, league_id, realm_id, price, quantity, created_at)
VALUES (
    %(item_id)s, 
    %(league_id)s, 
    %(realm_id)s, 
    %(price)s, 
    %(quantity)s, 
    to_timestamp(%(created_at)s)
)
        """
        price_dict_list = [
            {**price.model_dump(), "created_at": epoch} for price in prices
        ]

        await cursor.executemany(query, price_dict_list)
