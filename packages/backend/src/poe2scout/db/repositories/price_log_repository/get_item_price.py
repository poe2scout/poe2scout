import logging
from datetime import datetime, timezone

from ..base_repository import BaseRepository, RepositoryModel, scalar_as


class GetItemPriceModel(RepositoryModel):
    item_id: int
    league_id: int


logger = logging.getLogger(__name__)


async def get_item_price(
    item_id: int,
    league_id: int,
    realm_id: int,
    epoch: int | None,
) -> float:
    async with BaseRepository.get_db_cursor(row_factory=scalar_as(float)) as cursor:
        epoch = epoch or int(datetime.now(tz=timezone.utc).timestamp())

        query = """
            SELECT price FROM price_log
            WHERE item_id = %(item_id)s
              AND league_id = %(league_id)s
              AND realm_id = %(realm_id)s
              AND created_at < %(created_before)s
            ORDER BY created_at DESC
            LIMIT 1
        """

        params = {
            "item_id": item_id,
            "league_id": league_id,
            "realm_id": realm_id,
            "created_before": datetime.fromtimestamp(float(epoch)),
        }

        await cursor.execute(query, params)

        price = await cursor.fetchone()
        logger.info(
            f"Getting Item price for {item_id} in league {league_id} at "
            f"time {datetime.fromtimestamp(float(epoch))}. Price: {price}"
        )

        return price if price else 0