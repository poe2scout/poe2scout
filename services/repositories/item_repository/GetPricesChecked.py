from typing import Optional, Awaitable
from ..base_repository import BaseRepository

class GetPricesChecked(BaseRepository):
    async def execute(self, epoch: int, leagueId: int) -> bool:
        item_query = """
            SELECT
                CASE
                    WHEN EXISTS(
                        SELECT 1 FROM "PriceLog"
                        WHERE "createdAt" = to_timestamp(%s)
                        AND "leagueId" = %s
                    )
                    THEN 1
                    ELSE 0
                END;
        """

        return bool((await self.execute_query(
            item_query, (epoch, leagueId)))[0]['case'])
        
