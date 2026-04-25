from datetime import date

from psycopg.rows import class_row

from ..base_repository import BaseRepository, RepositoryModel


class DailyStatsHistoryEntry(RepositoryModel):
    day: date
    open_price: float
    close_price: float
    min_price: float
    max_price: float
    avg_price: float


async def get_item_daily_stats_history(
    item_id: int,
    league_id: int,
    realm_id: int,
    limit: int,
    end_date: date | None,
) -> list[DailyStatsHistoryEntry]:
    async with BaseRepository.get_db_cursor(
        row_factory=class_row(DailyStatsHistoryEntry),
    ) as cursor:
        query = """
SELECT
    day,
    open_price,
    close_price,
    min_price,
    max_price,
    avg_price
FROM item_daily_stats
WHERE item_id = %(item_id)s
AND league_id = %(league_id)s
AND realm_id = %(realm_id)s
AND (%(end_date)s::date IS NULL OR day < %(end_date)s::date)
ORDER BY day DESC
LIMIT %(limit)s;
        """

        params = {
            "item_id": item_id,
            "league_id": league_id,
            "realm_id": realm_id,
            "end_date": end_date,
            "limit": limit,
        }

        await cursor.execute(query, params)

        return await cursor.fetchall()
