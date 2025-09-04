from typing import Optional, List, Dict
from ..base_repository import BaseRepository
from pydantic import BaseModel
from datetime import datetime, timedelta


class PriceLogEntry(BaseModel):
    price: float
    time: datetime
    quantity: int


class GetItemPriceHistory(BaseRepository):
    async def execute(self, itemId: int, leagueId: int, logCount: int, logFrequency: int) -> Dict[str, List[PriceLogEntry]]:
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

        current_block_start = now.replace(
            hour=(now.hour // logFrequency) * logFrequency,
            minute=0,
            second=0,
            microsecond=0
        )

        overall_start_time = current_block_start - timedelta(hours=(logCount - 1) * logFrequency)

        price_log_query = """
            WITH relevant_logs AS (
                SELECT 
                    price,
                    quantity,
                    "createdAt" as time,
                    -- Assign each log to a time bucket and find the latest one in each bucket
                    ROW_NUMBER() OVER (
                        PARTITION BY date_bin((%(logFrequency)s || ' hours')::interval, "createdAt", %(current_block_start)s::timestamp) 
                        ORDER BY "createdAt" DESC
                    ) as rn
                FROM "PriceLog"
                WHERE 
                    "itemId" = %(itemId)s
                    AND "leagueId" = %(leagueId)s
                    -- Pre-filter to only scan logs within the total time window of the chart
                    AND "createdAt" >= %(overall_start_time)s
            )
            SELECT 
                price,
                quantity,
                -- Standardize the timestamp to the start of its bucket for consistent output
                date_bin((%(logFrequency)s || ' hours')::interval, time, %(current_block_start)s::timestamp) as time
            FROM relevant_logs
            WHERE rn = 1
            ORDER BY time DESC;
        """

        query_params = {
            "logFrequency": logFrequency,         
            "current_block_start": current_block_start,  
            "itemId": itemId,
            "leagueId": leagueId,
            "overall_start_time": overall_start_time
        }

        price_logs = await self.execute_query(price_log_query, query_params)

        price_history = [
            PriceLogEntry.model_construct(
                price=log["price"],
                time=log["time"],
                quantity=log["quantity"]
            )
            for log in price_logs
        ]

        return {'price_history': price_history}