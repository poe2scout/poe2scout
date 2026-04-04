from ..base_repository import BaseRepository, scalar_as


async def get_items_in_current_league(league_id: int) -> list[int]:
    async with BaseRepository.get_db_cursor(row_factory=scalar_as(int)) as cursor:
        query = """
            SELECT i.item_id
            FROM item as i
            WHERE EXISTS (
            SELECT 1
            FROM price_log as pl
            WHERE pl.item_id = i.item_id
            AND pl.league_id = %s
            );
        """
        await cursor.execute(query, (league_id,))

        return await cursor.fetchall()
