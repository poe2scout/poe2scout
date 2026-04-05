from datetime import datetime, timedelta

from ..base_repository import BaseRepository, scalar_as


async def get_fetched_item_ids(current_hour: str, league_id: int) -> list[int]:
    async with BaseRepository.get_db_cursor(row_factory=scalar_as(int)) as cursor:
        current_hour_int = int(current_hour)
        ranges = [[0, 12], [12, 24]]

        current_start = None
        current_end = None
        for hour_range in ranges:
            if current_hour_int >= hour_range[0] and current_hour_int < hour_range[1]:
                current_start = hour_range[0]
                current_end = hour_range[1]

        assert current_start is not None and current_end is not None

        current_start = datetime.now().replace(
            hour=current_start, minute=0, second=0, microsecond=0
        )
        current_day = datetime.now().day
        if current_end == 24:
            current_end = 0
            current_day = (datetime.now() + timedelta(days=1)).day
        current_end = datetime.now().replace(
            day=current_day, hour=current_end, minute=0, second=0, microsecond=0
        )

        query = """
            SELECT DISTINCT i.item_id FROM item as i
            JOIN price_log as pl ON i.item_id = pl.item_id
            JOIN league as l ON pl.league_id = l.league_id
            WHERE pl.created_at > %s AND pl.created_at < %s AND l.league_id = %s
        """
        await cursor.execute(query, (current_start, current_end, league_id))

        return await cursor.fetchall()