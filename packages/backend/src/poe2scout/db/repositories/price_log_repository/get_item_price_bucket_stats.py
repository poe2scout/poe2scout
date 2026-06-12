from datetime import datetime

from psycopg.rows import class_row

from poe2scout.db.repositories.models import PriceLogEntry

from ..base_repository import BaseRepository, RepositoryModel


class GetItemPriceBucketStatsDto(RepositoryModel):
    item_id: int
    block_index: int
    price: float | None
    quantity: int | None
    time: datetime


async def get_item_price_bucket_stats(
    item_ids: list[int],
    league_id: int,
    realm_id: int,
    bucket_starts: list[datetime],
    frequency_hours: int,
) -> dict[int, list[PriceLogEntry | None]]:
    if not item_ids or not bucket_starts:
        return {}

    async with BaseRepository.get_db_cursor(
        row_factory=class_row(GetItemPriceBucketStatsDto),
    ) as cursor:
        query = """
            WITH time_blocks AS (
                SELECT
                    block_start,
                    block_start + (%(frequency_hours)s * interval '1 hour') AS block_end,
                    block_index
                FROM unnest(
                    %(block_starts)s::timestamp[],
                    %(block_indices)s::int[]
                ) AS tb(block_start, block_index)
            ),
            item_blocks AS (
                SELECT
                    item_id,
                    tb.block_start,
                    tb.block_end,
                    tb.block_index
                FROM unnest(%(item_ids)s::int[]) AS req(item_id)
                CROSS JOIN time_blocks tb
            )
            SELECT
                ib.item_id AS "item_id",
                ib.block_index AS "block_index",
                bucket.price AS "price",
                bucket.quantity AS "quantity",
                ib.block_start AS "time"
            FROM item_blocks ib
            LEFT JOIN LATERAL (
                SELECT
                    avg(pl.price)::double precision AS price,
                    sum(pl.quantity)::int AS quantity
                FROM price_log pl
                WHERE pl.item_id = ib.item_id
                  AND pl.league_id = %(league_id)s
                  AND pl.realm_id = %(realm_id)s
                  AND pl.created_at >= ib.block_start
                  AND pl.created_at < ib.block_end
            ) AS bucket ON TRUE
            ORDER BY ib.item_id, ib.block_index;
        """

        params = {
            "block_starts": bucket_starts,
            "block_indices": list(range(len(bucket_starts))),
            "item_ids": item_ids,
            "league_id": league_id,
            "realm_id": realm_id,
            "frequency_hours": frequency_hours,
        }

        await cursor.execute(query, params)

        results: dict[int, list[PriceLogEntry | None]] = {
            item_id: [None] * len(bucket_starts) for item_id in item_ids
        }

        price_logs = await cursor.fetchall()
        for log in price_logs:
            if log.price is None or log.quantity is None:
                continue

            results[log.item_id][log.block_index] = PriceLogEntry.model_construct(
                price=log.price,
                time=log.time,
                quantity=log.quantity,
            )

        return results
