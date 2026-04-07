from ..base_repository import BaseRepository, scalar_as


async def get_items_in_current_league(league_id: int, realm_id: int) -> list[int]:
    async with BaseRepository.get_db_cursor(row_factory=scalar_as(int)) as cursor:
        query = """
            SELECT DISTINCT pl.item_id
              FROM price_log AS pl
             WHERE pl.league_id = %s
               AND pl.realm_id = %s;
        """
        await cursor.execute(query, (league_id, realm_id))

        return await cursor.fetchall()
