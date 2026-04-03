from typing import Optional, List, Dict

from psycopg.rows import class_row
from pydantic import BaseModel
from ..base_repository import BaseRepository

class AverageUniquePrice(BaseModel):
    baseItemId: int
    average_price: float

class GetAverageUniquePrice(BaseRepository):
    async def execute(
        self, itemIds: List[int], leagueId: int
    ) -> Dict[int, Optional[float]]:
        async with self.get_db_cursor(
            rowFactory=class_row(AverageUniquePrice)
        ) as cursor:
            query = """
                WITH unique_item_ids AS (
                    SELECT ib.id as "baseItemId", ui."itemId"
                    FROM "Item" as ib
                    JOIN "BaseItem" as bi on ib."baseItemId" = bi.id
                    JOIN "Item" ON "Item"."baseItemId" = bi.id AND "Item"."itemType" = 'unique'
                    JOIN "UniqueItem" as ui ON ui."itemId" = "Item".id
                    WHERE ib.id = ANY(%s) AND ui."isChanceable" = TRUE
                ),
                latest_prices AS (
                    SELECT DISTINCT ON (pl."itemId") 
                        ui."baseItemId",
                        pl."itemId",
                        pl.price
                    FROM "PriceLog" as pl
                    JOIN unique_item_ids ui ON ui."itemId" = pl."itemId"
                    WHERE pl."leagueId" = %s
                    ORDER BY pl."itemId", pl."createdAt" DESC
                )
                SELECT "baseItemId"
                    , AVG(price) as average_price
                FROM latest_prices
                GROUP BY "baseItemId";
            """

            # Execute the query
            await cursor.execute(query, (itemIds, leagueId))
            # Convert results to dictionary
            results = {row.baseItemId: row.average_price for row in await cursor.fetchall()}

            # Ensure all requested itemIds have a value (None if no data found)
            return {item_id: results.get(item_id) for item_id in itemIds}
