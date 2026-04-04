from datetime import datetime

from psycopg.rows import class_row

from poe2scout.db.repositories.models import PriceLogEntry

from ..base_repository import BaseRepository, RepositoryModel


class GetItemPriceHistoryModel(RepositoryModel):
    price_history: list[PriceLogEntry]
    has_more: bool


async def get_item_price_history(
    item_id: int,
    league_id: int,
    log_count: int,
    log_frequency: int,
    end_time: datetime,
) -> GetItemPriceHistoryModel:
    async with BaseRepository.get_db_cursor(row_factory=class_row(PriceLogEntry)) as cursor:
        limit = log_count + 1

        query = """
SELECT DISTINCT ON (time)
    price,
    quantity,
    date_bin(
        (%(log_frequency)s || ' hours')::interval,
        "createdAt",
        %(end_time)s::timestamp
    ) AS time
FROM "PriceLog"
WHERE "itemId" = %(item_id)s
AND "leagueId" = %(league_id)s
AND "createdAt" < %(end_time)s
ORDER BY time DESC, "createdAt" DESC
LIMIT %(limit)s;
        """

        params = {
            "log_frequency": log_frequency,
            "end_time": end_time,
            "item_id": item_id,
            "league_id": league_id,
            "limit": limit,
        }

        await cursor.execute(query, params)

        price_logs = await cursor.fetchall()

        has_more = len(price_logs) > log_count

        if has_more:
            price_logs = price_logs[:log_count]

        price_history = [
            PriceLogEntry.model_construct(
                price=log.price, time=log.time, quantity=log.quantity
            )
            for log in price_logs
        ]

        return GetItemPriceHistoryModel(price_history=price_history, has_more=has_more)
