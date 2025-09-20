from datetime import datetime, timezone
import logging
from ..base_repository import BaseRepository
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
        epoch = epoch or int(datetime.now(tz=timezone.utc).timestamp())
        
        item_query = """
            SELECT "price" FROM "PriceLog"
            WHERE "itemId" = %(itemId)s AND "leagueId" = %(leagueId)s AND "createdAt" < %(createdBefore)s
            ORDER BY "createdAt" DESC
            LIMIT 1
        """

        params = {
            "itemId": itemId,
            "leagueId": leagueId,
            "createdBefore": datetime.fromtimestamp(float(epoch)),
        }


        price = await self.execute_query(item_query, params)

        logger.info(f"Getting Item price for {itemId} in league {leagueId} at time {datetime.fromtimestamp(float(epoch))}. Price: {price}")

        if len(price) == 0:
            return 0  # Default div price in exalts. This method is / should only be called to get divine price or chaos price.
        else:
            return price[0]["price"]
