from poe2scout.db.repositories import price_log_repository
from poe2scout.db.repositories.price_log_repository.record_price import RecordPriceModel
import logging


logger = logging.getLogger(__name__)


async def record_price(
    price: float, 
    item_id: int, 
    league_id: int, 
    quantity: int, 
):
    if price <= 0:
        logger.info(
            f"Price is 0 or less, skipping record_price for {item_id} in {league_id}"
        )
        return
    logger.info(
        f"Recording price for {item_id} in {league_id}: {price} with quantity {quantity}"
    )
    await price_log_repository.record_price(
        RecordPriceModel(
            item_id=item_id, league_id=league_id, price=price, quantity=quantity
        )
    )
