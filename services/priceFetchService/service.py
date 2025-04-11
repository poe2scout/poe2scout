from services.repositories.item_repository import ItemRepository
from httpx import AsyncClient
from .functions.fetch_unique import PriceFetchResult, DivinePriceFetchResult, fetch_unique, fetch_unique_divine
from .functions.record_price import record_price
from .functions.fetch_currency import fetch_currency
import logging
from .config import PriceFetchConfig
from services.repositories.base_repository import BaseRepository
from .functions.sync_metadata_and_icon import sync_metadata_and_icon
from datetime import datetime, timedelta
from services.libs.poe_trade_client import PoeTradeClient
from services.repositories.item_repository.GetAllUniqueItems import UniqueItem
from services.repositories.item_repository.GetAllCurrencyItems import CurrencyItem
from services.repositories.item_repository.GetLeagues import League
import asyncio
logger = logging.getLogger(__name__)

async def run(config: PriceFetchConfig, repo: ItemRepository):
    # Define the schedule

    logger.info(f"Price fetch service started.")



    await FetchPrices(config, repo)





def choose_currency(exalt_price_info: PriceFetchResult, divines_price_info: DivinePriceFetchResult) -> bool:

    if exalt_price_info.price <= 0:
        should_use_exalt = False
        return should_use_exalt
    
    if divines_price_info.price <= 0:
        should_use_exalt = True
        return should_use_exalt
    
    if exalt_price_info.price and exalt_price_info.quantity >= 3:
        # Convert exalt prices to divine equivalent
        ex_price = exalt_price_info.price / \
            divines_price_info.price
        divine_search_price = divines_price_info.price
        
        logger.info(
            f"Exalt price: {ex_price} divs, Divine search price: {divine_search_price} divs")

        # Use exalt prices if they're cheaper
        if ex_price <= divine_search_price:
            should_use_exalt = True
        else:
            should_use_exalt = False
    else:
        should_use_exalt = False
    return should_use_exalt


async def FetchPrices(config: PriceFetchConfig, repo: ItemRepository):

    # Get all unqiue items
    leagues = await repo.GetLeagues()
    baseUniqueItems = await repo.GetAllUniqueItems()
    baseCurrencyItems = await repo.GetAllCurrencyItems()

    exaltedItem = await repo.GetCurrencyItem("exalted")
    divineItem = await repo.GetCurrencyItem("divine")

    headers = {
        "User-Agent": "POE2SCOUT (contact: b@girardet.co.nz)"
    }
    # Create a client
    async with PoeTradeClient(headers=headers) as client:
        for league in leagues:
            current_time =  datetime.now().strftime("%H")
            fetchedItemIds: list[int] = await repo.GetFetchedItemIds(current_time, league.id)
            itemIds = await repo.GetAllItems()
            itemIds = [item.id for item in itemIds if item.id not in fetchedItemIds]

            itemIdsToFetch = [item for item in itemIds if item not in fetchedItemIds]

            uniqueItems = [item for item in baseUniqueItems if item.itemId in itemIdsToFetch]
            currencyItems = [item for item in baseCurrencyItems if item.itemId in itemIdsToFetch]

            if len(itemIdsToFetch) == 0:
                logger.info(f"No items to fetch")
                continue
                
            logger.info(f"Fetching prices for {len(itemIdsToFetch)} items")

            divinePrice = await repo.GetItemPrice(divineItem.itemId, league.id)

            inListDivine = [item for item in currencyItems if item.itemId == divineItem.itemId]
            if len(inListDivine) != 0:
                listDivine = inListDivine[0]
                logger.info(f"Fetching divine price for {listDivine.text} in {league.value}")
                currencyItems.remove(listDivine)
                newDivinePrice = await fetch_currency(want_currency=listDivine, league=league, have_currency_api_ids=[exaltedItem.apiId], client=client, divine_price=divinePrice)
                logger.info(f"New divine price: {newDivinePrice.price}, quantity: {newDivinePrice.quantity}")
                await record_price(newDivinePrice.price, listDivine.itemId, league.id, newDivinePrice.quantity, repo)
            else:
                logger.info(f"No dviine item in currency list")

            inListExalted = [item for item in currencyItems if item.itemId == exaltedItem.itemId]
            if len(inListExalted) != 0:
                listExalted = inListExalted[0]
                logger.info(f"Fetching exalted price for {listExalted.text} in {league.value}")
                currencyItems.remove(listExalted)
                await record_price(1, listExalted.itemId, league.id, 1, repo)
            else:
                logger.info(f"No exalted item in currency list")

            divinePrice = await repo.GetItemPrice(divineItem.itemId, league.id)

            await asyncio.gather(
                process_uniques(uniqueItems, league, repo, client, exaltedItem, divineItem, divinePrice),
                process_currency(currencyItems, league, repo, client, exaltedItem, divineItem, divinePrice)
            )   
            currencyItems.append(divineItem)
            currencyItems.append(exaltedItem)

            for currencyItem in currencyItems:
                if currencyItem.itemMetadata is None:
                    logger.info(f"Syncing metadata and icon for {currencyItem.text}")
                    await sync_metadata_and_icon(currencyItem, repo, client, BASE_URL, REALM, league.value)



BASE_URL = "https://www.pathofexile.com/api/trade2"
REALM = "poe2"

async def process_uniques(uniqueItems: list[UniqueItem], league: League, repo: ItemRepository, client: PoeTradeClient, exaltedItem: CurrencyItem, divineItem: CurrencyItem, divinePrice: float):
    for uniqueItem in uniqueItems:
        logger.info(f"Fetching price for {uniqueItem.name} in {league.value}")
        exalt_price_info: PriceFetchResult = await fetch_unique(uniqueItem, league, repo, client)
        logger.info(f"Exalt price info: {exalt_price_info}")
        should_use_exalt = True

        if exalt_price_info.should_fetch_divines:
            logger.info(f"Fetching divines price for {uniqueItem.name} in {league.value}")
            divines_price_info: DivinePriceFetchResult = await fetch_unique_divine(uniqueItem, league, client, repo)
            
            should_use_exalt = choose_currency(exalt_price_info, divines_price_info)

        (price, currencyItemId, quantity) = (exalt_price_info.price, exaltedItem.itemId, exalt_price_info.quantity) if should_use_exalt else (divines_price_info.price*divinePrice, divineItem.itemId, (exalt_price_info.quantity+ divines_price_info.quantity))
        logger.info(f"Recording price for {uniqueItem.name} in {league.value} with price {price} and quantity {quantity}")
        await record_price(price, uniqueItem.itemId, league.id, quantity, repo)
            
async def process_currency(currencyItems: list[CurrencyItem], league: League, repo: ItemRepository, client: PoeTradeClient, exaltedItem: CurrencyItem, divineItem: CurrencyItem, divinePrice: float):
    for currencyItem in currencyItems:
        logger.info(f"Fetching price for {currencyItem.text} in {league.value}")
        price_result = await fetch_currency(want_currency=currencyItem, league=league, have_currency_api_ids=[exaltedItem.apiId], divine_price=divinePrice, client=client)
        logger.info(f"Price: {price_result.price}, quantity: {price_result.quantity}")

        if price_result.quantity < 3:
            divine_price_result = await fetch_currency(want_currency=currencyItem, league=league, have_currency_api_ids=[divineItem.apiId], divine_price=divinePrice, client=client)

            if divine_price_result.quantity >= price_result.quantity:
                price_result = divine_price_result

        await record_price(price_result.price, currencyItem.itemId, league.id, price_result.quantity, repo)
