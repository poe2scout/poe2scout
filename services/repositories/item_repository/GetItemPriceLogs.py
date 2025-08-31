from typing import Optional, List, Dict
from ..base_repository import BaseRepository
from pydantic import BaseModel
from datetime import datetime, timedelta
import time


class PriceLogEntry(BaseModel):
    price: float
    time: datetime
    quantity: int


class GetItemPriceLogs(BaseRepository):
    async def execute(self, itemIds: List[int], leagueId: int) -> Dict[int, List[Optional[PriceLogEntry]]]:

        now = datetime.now()
        current_block = now.replace(
            hour=(now.hour // 6) * 6,
            minute=0,
            second=0,
            microsecond=0
        )

        # Generate time blocks once
        time_blocks = [current_block - timedelta(hours=i*6) for i in range(7)]

        # Let PostgreSQL do the heavy lifting - finding the latest price log in each time block
        price_log_query = """
            WITH time_blocks AS (
                SELECT 
                    block_start,
                    block_start + interval '6 hours' as block_end,
                    block_index
                FROM unnest(%s::timestamp[], %s::int[]) AS tb(block_start, block_index)
            ),
            item_blocks AS (
                SELECT 
                    i.item_id,
                    tb.block_start,
                    tb.block_end,
                    tb.block_index
                FROM time_blocks tb
                CROSS JOIN unnest(%s::int[]) AS i(item_id)
            ),
            latest_prices AS (
                SELECT 
                    ib.item_id,
                    ib.block_start,
                    ib.block_index,
                    pl."price",
                    ROW_NUMBER() OVER (
                        PARTITION BY ib.item_id, ib.block_start
                        ORDER BY pl."createdAt" DESC
                    ) as rn,
                    pl."quantity"
                FROM item_blocks ib
                LEFT JOIN "PriceLog" pl ON 
                    pl."itemId" = ib.item_id
                    AND pl."leagueId" = %s
                    AND pl."createdAt" >= ib.block_start
                    AND pl."createdAt" < ib.block_end
            )
            SELECT 
                item_id as "itemId",
                block_index as "blockIndex",
                price,
                quantity,
                block_start as "time"
            FROM latest_prices
            WHERE rn = 1
            ORDER BY item_id, block_index;
        """

        # Prepare block timestamps and indices
        block_timestamps = [tb for tb in time_blocks]
        block_indices = list(range(7))

        # Execute the query
        price_logs = await self.execute_query(
            price_log_query,
            (
                block_timestamps,
                block_indices,
                itemIds,
                leagueId
            )
        )

        # Process results efficiently
        results = {item_id: [None] * 7 for item_id in itemIds}

        # Fill in actual results where we have data
        for log in price_logs:
            if log["price"] is not None:
                item_id = log["itemId"]
                block_index = log["blockIndex"]
                results[item_id][block_index] = PriceLogEntry(
                    price=log["price"],
                    time=log["time"],
                    quantity=log["quantity"]
                )

        return results
