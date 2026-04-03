from typing import List
from psycopg.rows import class_row
from pydantic import BaseModel
from datetime import datetime

from poe2scout.db.repositories.base_repository import BaseRepository
from poe2scout.db.repositories.models import PriceLogEntry


class GetItemPriceHistoryModel(BaseModel):
    price_history: List[PriceLogEntry]
    has_more: bool


class GetItemPriceHistory(BaseRepository):
    async def execute(
        self,
        itemId: int,
        leagueId: int,
        logCount: int,
        logFrequency: int,
        endTime: datetime,
    ) -> GetItemPriceHistoryModel:
        async with self.get_db_cursor(
            rowFactory=class_row(PriceLogEntry)
        ) as cursor:

            limit = logCount + 1

            query = """
    SELECT DISTINCT ON (time)
        price,
        quantity,
        date_bin(
            (%(logFrequency)s || ' hours')::interval,
            "createdAt",
            %(endTime)s::timestamp
        ) AS time
    FROM "PriceLog"
    WHERE "itemId" = %(itemId)s
    AND "leagueId" = %(leagueId)s
    AND "createdAt" < %(endTime)s
    ORDER BY time DESC, "createdAt" DESC
    LIMIT %(limit)s;
            """

            params = {
                "logFrequency": logFrequency,
                "endTime": endTime,
                "itemId": itemId,
                "leagueId": leagueId,
                "limit": limit,
            }

            await cursor.execute(query, params)

            price_logs = await cursor.fetchall()

            has_more = len(price_logs) > logCount

            if has_more:
                price_logs = price_logs[:logCount]

            price_history = [
                PriceLogEntry.model_construct(
                    price=log.price, time=log.time, quantity=log.quantity
                )
                for log in price_logs
            ]

            return GetItemPriceHistoryModel(price_history=price_history, has_more=has_more)
