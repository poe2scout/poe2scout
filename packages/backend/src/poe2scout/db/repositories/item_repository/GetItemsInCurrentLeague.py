from typing import List

from ..base_repository import BaseRepository, scalar_as


class GetItemsInCurrentLeague(BaseRepository):
    async def execute(self, leagueId: int) -> List[int]:
        async with self.get_db_cursor(
            rowFactory=scalar_as(int)
        ) as cursor:
            query = """
                SELECT i."id"
                FROM "Item" as i
                WHERE EXISTS (
                SELECT 1
                FROM "PriceLog" as pl
                WHERE pl."itemId" = i."id"
                AND pl."leagueId" = %s
                );
            """
            await cursor.execute(query, (leagueId,))

            return await cursor.fetchall()
