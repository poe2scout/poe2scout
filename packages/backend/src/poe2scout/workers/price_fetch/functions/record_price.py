from poe2scout.db.repositories.item_repository import ItemRepository
from poe2scout.db.repositories.item_repository.record_price import RecordPriceModel
import logging

logger = logging.getLogger(__name__)


async def record_price(
    price: float, item_id: int, league_id: int, quantity: int, repo: ItemRepository
):
    if price <= 0:
        logger.info(
            f"Price is 0 or less, skipping record_price for {item_id} in {league_id}"
        )
        return
    logger.info(
        f"Recording price for {item_id} in {league_id}: {price} with quantity {quantity}"
    )
    await repo.record_price(
        RecordPriceModel(
            item_id=item_id, league_id=league_id, price=price, quantity=quantity
        )
    )
