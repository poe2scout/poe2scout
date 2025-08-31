from typing import Optional, List, Dict
from ..base_repository import BaseRepository
from pydantic import BaseModel
from datetime import datetime, timedelta
import time


class PriceLogEntry(BaseModel):
    price: float
    time: datetime
    quantity: int


class GetItemPriceHistory(BaseRepository):
    async def execute(self, itemId: int, leagueId: int, logCount: int, logFrequency: int) -> Dict[str, List[Optional[PriceLogEntry]]]:
        lastLogTimeQuery = """
            SELECT pl."createdAt"
              FROM "PriceLog" AS pl
             WHERE pl."itemId" = %s
               AND pl."leagueId" = %s
             ORDER BY pl."createdAt" DESC
             LIMIT 1
            """
        
        lastTime = await self.execute_query(lastLogTimeQuery, (itemId, leagueId))

        if len(lastTime) == 1:
            now = lastTime[0]['createdAt']
        else:
            now = datetime.now()

        current_block = now.replace(
            hour=(now.hour // logFrequency) * logFrequency,
            minute=0,
            second=0,
            microsecond=0
        )

        # Generate time blocks once
        time_blocks = [current_block - timedelta(hours=i*logFrequency) for i in range(logCount)]

        # Prepare block timestamps and indices
        block_timestamps = [tb for tb in time_blocks]
        block_indices = list(range(logCount))

        # Let PostgreSQL do the heavy lifting - finding the latest price log in each time block
        price_log_query = """
            WITH time_blocks AS (
                SELECT 
                    block_start,
                    block_start + (%s || ' hours')::interval as block_end,
                    block_index
                FROM unnest(%s::timestamp[], %s::int[]) AS tb(block_start, block_index)
            ),
            latest_prices AS (
                SELECT 
                    tb.block_start,
                    tb.block_index,
                    pl."price",
                    ROW_NUMBER() OVER (
                        PARTITION BY tb.block_start
                        ORDER BY pl."createdAt" DESC
                    ) as rn,
                    pl."quantity"
                FROM time_blocks tb
                LEFT JOIN "PriceLog" pl ON 
                    pl."itemId" = %s
                    AND pl."leagueId" = %s
                    AND pl."createdAt" >= tb.block_start
                    AND pl."createdAt" < tb.block_end
            )
            SELECT 
                block_index as "blockIndex",
                price,
                quantity,
                block_start as "time"
            FROM latest_prices
            WHERE rn = 1
            ORDER BY block_index;
        """

        # Execute the query
        price_logs = await self.execute_query(
            price_log_query,
            (
                logFrequency,
                block_timestamps,
                block_indices,
                itemId,
                leagueId
            )
        )

        # Process results efficiently
        results = {'price_history': [None] * logCount}

        # Fill in actual results where we have data
        for log in price_logs:
            if log["price"] is not None:
                block_index = log["blockIndex"]
                results['price_history'][block_index] = PriceLogEntry(
                    price=log["price"],
                    time=log["time"],
                    quantity=log["quantity"]
                )

        return results
