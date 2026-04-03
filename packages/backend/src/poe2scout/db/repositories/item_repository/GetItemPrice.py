from datetime import datetime, timezone
import logging
from ..base_repository import BaseRepository, scalar_as
from pydantic import BaseModel


class GetItemPriceModel(BaseModel):
    itemId: int
    leagueId: int

logger = logging.getLogger(__name__)

class GetItemPrice(BaseRepository):
    async def execute(
        self,
        itemId: int,
        leagueId: int,
        epoch: int | None = None    
    ) -> float:
        async with self.get_db_cursor(
            rowFactory=scalar_as(float)
        ) as cursor:
            epoch = epoch or int(datetime.now(tz=timezone.utc).timestamp())
            
            query = """
                SELECT "price" FROM "PriceLog"
                WHERE "itemId" = %(itemId)s 
                AND "leagueId" = %(leagueId)s 
                AND "createdAt" < %(createdBefore)s
                ORDER BY "createdAt" DESC
                LIMIT 1
            """

            params = {
                "itemId": itemId,
                "leagueId": leagueId,
                "createdBefore": datetime.fromtimestamp(float(epoch)),
            }


            await cursor.execute(query, params)

            price = await cursor.fetchone()
            logger.info(f"Getting Item price for {itemId} in league {leagueId} at " +\
                        f"time {datetime.fromtimestamp(float(epoch))}. Price: {price}")

            return price if price else 0
