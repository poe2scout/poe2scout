from services.repositories.item_repository import ItemRepository
from services.repositories.item_repository.RecordPrice import RecordPriceModel
import logging
logger = logging.getLogger(__name__)

async def record_price(price: float, itemId: int, leagueId: int, quantity: int, repo: ItemRepository):
    if price <= 0:
        logger.info(f"Price is 0 or less, skipping record_price for {itemId} in {leagueId}")
        return
    logger.info(f"Recording price for {itemId} in {leagueId}: {price} with quantity {quantity}")
    await repo.RecordPrice(RecordPriceModel(
        itemId=itemId,
        leagueId=leagueId,
        price=price,
        quantity=quantity
    ))
