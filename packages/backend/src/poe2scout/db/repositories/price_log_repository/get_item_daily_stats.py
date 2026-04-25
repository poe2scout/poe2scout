from datetime import date

from psycopg.rows import class_row

from ..base_repository import BaseRepository, RepositoryModel


class GetItemDailyStatsDto(RepositoryModel):
    item_id: int
    avg_price: float
    data_points: int
    day: date


async def get_item_daily_stats(
    item_ids: list[int],
    league_id: int,
    realm_id: int,
    dates: list[date],
) -> list[GetItemDailyStatsDto]:
    if not item_ids or not dates:
        return []

    async with BaseRepository.get_db_cursor(
        row_factory=class_row(GetItemDailyStatsDto),
    ) as cursor:
        query = """
            SELECT ids.item_id
                 , ids.avg_price
                 , ids.data_points
                 , ids.day
              FROM item_daily_stats ids
             WHERE ids.day = ANY(%(dates)s::date[])
               AND ids.item_id = ANY(%(item_ids)s::int[])
               AND ids.realm_id = %(realm_id)s
               AND ids.league_id = %(league_id)s
        """

        params = {
            "dates": dates,
            "item_ids": item_ids,
            "league_id": league_id,
            "realm_id": realm_id,
        }

        await cursor.execute(query, params)

        return await cursor.fetchall()
