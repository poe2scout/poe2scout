from datetime import datetime, timedelta

from psycopg.rows import class_row

from poe2scout.db.repositories.models import PriceLogEntry

from ..base_repository import BaseRepository, RepositoryModel


class GetItemPriceLogsDto(RepositoryModel):
    item_id: int
    block_index: int
    price: float | None
    quantity: int | None
    time: datetime


async def get_item_price_logs(
    item_ids: list[int], 
    league_id: int,
    realm_id: int
) -> dict[int, list[PriceLogEntry | None]]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(GetItemPriceLogsDto)) as cursor:
        now = datetime.now()
        current_block = now.replace(
            hour=(now.hour // 6) * 6, minute=0, second=0, microsecond=0
        )

        time_blocks = [current_block - timedelta(hours=i * 6) for i in range(7)]

        query = """
            WITH time_blocks AS (
                SELECT
                    block_start,
                    block_start + interval '6 hours' as block_end,
                    block_index
                FROM unnest(%(block_timestamps)s::timestamp[], %(block_indices)s::int[]) AS tb(block_start, block_index)
            ),
            item_blocks AS (
                SELECT
                    i.item_id,
                    tb.block_start,
                    tb.block_end,
                    tb.block_index
                FROM time_blocks tb
                CROSS JOIN unnest(%(item_ids)s::int[]) AS i(item_id)
            ),
            latest_prices AS (
                SELECT
                    ib.item_id,
                    ib.block_start,
                    ib.block_index,
                    pl."price",
                    ROW_NUMBER() OVER (
                        PARTITION BY ib.item_id, ib.block_start
                        ORDER BY pl.created_at DESC
                    ) as rn,
                    pl."quantity"
                FROM item_blocks ib
                LEFT JOIN price_log pl ON
                    pl.item_id = ib.item_id
                    AND pl.league_id = %(league_id)s
                    AND pl.realm_id = %(realm_id)s
                    AND pl.created_at >= ib.block_start
                    AND pl.created_at < ib.block_end
            )
            SELECT
                item_id as "item_id",
                block_index as "block_index",
                price,
                quantity,
                block_start as "time"
            FROM latest_prices
            WHERE rn = 1
            ORDER BY item_id, block_index;
        """

        block_timestamps = [tb for tb in time_blocks]
        block_indices = list(range(7))

        params = {
            "block_timestamps": block_timestamps,
            "block_indices": block_indices,
            "item_ids": item_ids,
            "league_id": league_id,
            "realm_id": realm_id
        }

        await cursor.execute(query, params)

        results: dict[int, list[PriceLogEntry | None]] = {
            item_id: [None] * 7 for item_id in item_ids
        }

        price_logs = await cursor.fetchall()

        for log in price_logs:
            if log.price is not None and log.quantity is not None:
                results[log.item_id][log.block_index] = PriceLogEntry(
                    price=log.price,
                    time=log.time,
                    quantity=log.quantity,
                )

        return results

