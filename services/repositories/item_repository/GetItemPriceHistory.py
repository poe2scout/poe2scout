from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

from services.repositories.base_repository import BaseRepository
from services.repositories.models import PriceLogEntry


class GetItemPriceHistoryModel(BaseModel):
    price_history: List[PriceLogEntry]
    has_more: bool


class GetItemPriceHistory(BaseRepository):
    async def execute(self, itemId: int, leagueId: int, logCount: int, logFrequency: int, endTime: datetime) -> GetItemPriceHistoryModel:
        limit = logCount + 1

        price_log_query = """
WITH ranked_logs AS (
  SELECT
    "itemId",
    price,
    quantity,
    "createdAt",
    ROW_NUMBER() OVER (
      PARTITION BY "itemId"
      ORDER BY "createdAt" DESC
    ) AS rn
  FROM "PriceLog"
  WHERE
    "leagueId" = 5
    AND "createdAt" < current_date
)
SELECT
  "itemId",
  price,
  quantity,
  "createdAt" as time
FROM ranked_logs
WHERE
  rn <= 24
ORDER BY
  "itemId",
  time DESC;

        """

        query_params = {
            "logFrequency": logFrequency,
            "endTime": endTime,
            "itemId": itemId,
            "leagueId": leagueId,
            "limit": limit
        }

        price_logs = await self.execute_query(price_log_query, query_params)

        has_more = len(price_logs) > logCount

        if has_more:
            price_logs = price_logs[:logCount]
        
        price_logs.reverse()

        price_history = [
            PriceLogEntry.model_construct(
                price=log["price"],
                time=log["time"],
                quantity=log["quantity"]
            )
            for log in price_logs
        ]
        
        return GetItemPriceHistoryModel(price_history=price_history, has_more=has_more)
