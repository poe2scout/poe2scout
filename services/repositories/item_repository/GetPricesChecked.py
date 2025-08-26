from typing import Optional, Awaitable
from ..base_repository import BaseRepository

class GetPricesChecked(BaseRepository):
    async def execute(self, epoch: int) -> bool:
        item_query = """
            SELECT
                CASE
                    WHEN EXISTS(
                        SELECT 1 FROM "PriceLog"
                        WHERE "createdAt" = to_timestamp(%s)
                    )
                    THEN 1
                    ELSE 0
                END;
        """

        return bool((await self.execute_query(
            item_query, (epoch,)))[0]['case'])
        
