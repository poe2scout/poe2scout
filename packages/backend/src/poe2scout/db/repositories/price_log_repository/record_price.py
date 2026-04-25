from ..base_repository import BaseRepository, RepositoryModel


class RecordPriceModel(RepositoryModel):
    item_id: int
    league_id: int
    price: float
    quantity: int
    realm_id: int


async def record_price(price: RecordPriceModel):
    async with BaseRepository.get_db_cursor() as cursor:
        query = """
WITH inserted_price_log AS (
    INSERT INTO price_log (item_id, league_id, realm_id, price, quantity, created_at)
    VALUES (%(item_id)s, %(league_id)s, %(realm_id)s, %(price)s, %(quantity)s, NOW())
    RETURNING item_id, league_id, realm_id, price, quantity, created_at
),
inserted_daily_stats AS (
    SELECT
        realm_id,
        item_id,
        league_id,
        created_at,
        price AS open_price,
        price AS close_price,
        price AS min_price,
        price AS max_price,
        price AS avg_price,
        1 AS data_points,
        quantity AS volume
    FROM inserted_price_log
)
INSERT INTO item_daily_stats (
    realm_id,
    item_id,
    league_id,
    day,
    open_price,
    close_price,
    min_price,
    max_price,
    avg_price,
    data_points,
    volume
)
SELECT
    inserted.realm_id,
    inserted.item_id,
    inserted.league_id,
    inserted.created_at::date AS day,
    inserted.open_price,
    inserted.close_price,
    inserted.min_price,
    inserted.max_price,
    inserted.avg_price,
    inserted.data_points,
    inserted.volume
FROM inserted_daily_stats AS inserted
ON CONFLICT (realm_id, item_id, league_id, day) DO UPDATE SET
    close_price = EXCLUDED.close_price,
    min_price = LEAST(item_daily_stats.min_price, EXCLUDED.min_price),
    max_price = GREATEST(item_daily_stats.max_price, EXCLUDED.max_price),
    avg_price = (
        (item_daily_stats.avg_price * item_daily_stats.data_points)
        + (EXCLUDED.avg_price * EXCLUDED.data_points)
    ) / (item_daily_stats.data_points + EXCLUDED.data_points),
    data_points = item_daily_stats.data_points + EXCLUDED.data_points,
    volume = item_daily_stats.volume + EXCLUDED.volume
        """

        await cursor.execute(query, price.model_dump())


async def record_price_bulk(prices: list[RecordPriceModel], epoch: int):
    if len(prices) == 0:
        raise ValueError("record_price_bulk requires at least one price")

    seen_price_keys = set()
    for price in prices:
        price_key = (price.realm_id, price.item_id, price.league_id)
        if price_key in seen_price_keys:
            raise ValueError(
                "record_price_bulk received multiple prices for the same "
                + "realm_id, item_id, and league_id"
            )
        seen_price_keys.add(price_key)

    async with BaseRepository.get_db_cursor() as cursor:
        query = """
WITH input_prices AS (
    SELECT
        item_id,
        league_id,
        realm_id,
        price,
        quantity,
        to_timestamp(%(created_at)s)::timestamp AS created_at
    FROM unnest(
        %(item_ids)s::int[],
        %(league_ids)s::int[],
        %(realm_ids)s::int[],
        %(prices)s::double precision[],
        %(quantities)s::int[]
    ) AS price_input(
        item_id,
        league_id,
        realm_id,
        price,
        quantity
    )
),
inserted_price_log AS (
    INSERT INTO price_log (item_id, league_id, realm_id, price, quantity, created_at)
    SELECT item_id, league_id, realm_id, price, quantity, created_at
    FROM input_prices
    RETURNING item_id, league_id, realm_id, price, quantity, created_at
),
inserted_daily_stats AS (
    SELECT
        realm_id,
        item_id,
        league_id,
        created_at,
        price AS open_price,
        price AS close_price,
        price AS min_price,
        price AS max_price,
        price AS avg_price,
        1 AS data_points,
        quantity AS volume
    FROM inserted_price_log
)
INSERT INTO item_daily_stats (
    realm_id,
    item_id,
    league_id,
    day,
    open_price,
    close_price,
    min_price,
    max_price,
    avg_price,
    data_points,
    volume
)
SELECT
    inserted.realm_id,
    inserted.item_id,
    inserted.league_id,
    inserted.created_at::date AS day,
    inserted.open_price,
    inserted.close_price,
    inserted.min_price,
    inserted.max_price,
    inserted.avg_price,
    inserted.data_points,
    inserted.volume
FROM inserted_daily_stats AS inserted
ON CONFLICT (realm_id, item_id, league_id, day) DO UPDATE SET
    close_price = EXCLUDED.close_price,
    min_price = LEAST(item_daily_stats.min_price, EXCLUDED.min_price),
    max_price = GREATEST(item_daily_stats.max_price, EXCLUDED.max_price),
    avg_price = (
        (item_daily_stats.avg_price * item_daily_stats.data_points)
        + (EXCLUDED.avg_price * EXCLUDED.data_points)
    ) / (item_daily_stats.data_points + EXCLUDED.data_points),
    data_points = item_daily_stats.data_points + EXCLUDED.data_points,
    volume = item_daily_stats.volume + EXCLUDED.volume
        """

        params = {
            "item_ids": [price.item_id for price in prices],
            "league_ids": [price.league_id for price in prices],
            "realm_ids": [price.realm_id for price in prices],
            "prices": [price.price for price in prices],
            "quantities": [price.quantity for price in prices],
            "created_at": epoch,
        }

        await cursor.execute(query, params)
