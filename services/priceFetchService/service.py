import math
from typing import Dict, List

from pydantic import BaseModel
from services.priceFetchService.models.CurrencyExchangeResponse import CurrencyExchangeResponse, LeagueCurrencyPairData
from services.repositories.item_repository import ItemRepository
from services.repositories.item_repository.RecordPrice import RecordPriceModel
from httpx import AsyncClient
from .functions.fetch_unique import PriceFetchResult, DivinePriceFetchResult, fetch_unique, fetch_unique_divine
from .functions.record_price import record_price
from .functions.fetch_currency import fetch_currency
from .functions.extract_base_item_metadata import extract_base_item_metadata
import logging
from .config import PriceFetchConfig
from services.repositories.base_repository import BaseRepository
from .functions.sync_metadata_and_icon import sync_metadata_and_icon
from datetime import datetime, timedelta, timezone
from services.libs.poe_trade_client import PoeApiClient, PoeTradeClient
from services.repositories.item_repository.GetAllUniqueItems import UniqueItem
from services.repositories.item_repository.GetAllCurrencyItems import CurrencyItem
from services.repositories.item_repository.GetAllUniqueBaseItems import UniqueBaseItem
from services.repositories.item_repository.GetLeagues import League
from .functions.fetch_base import fetch_base

import asyncio
logger = logging.getLogger(__name__)

async def run(config: PriceFetchConfig, repo: ItemRepository):
    # Define the schedule

    logger.info(f"Price fetch service started.")
    await asyncio.gather(FetchCurrencyExchangePrices(repo, config),
                        FetchPrices(repo))





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

class CurrencyPrice(BaseModel):
    itemId: str
    value: float # In exalts
    quantityTraded: int

async def FetchCurrencyExchangePrices(repo: ItemRepository, config: PriceFetchConfig):
    current_timestamp = int(datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0).timestamp() - 60* 60)
    
    headers = {
        "User-Agent": "POE2SCOUT (contact: b@girardet.co.nz)"
    }
    async with PoeApiClient(config.POEAPI_CLIENT_ID, config.POEAPI_CLIENT_SECRET, headers=headers) as client:
        while True:
            await asyncio.sleep(current_timestamp + 60 * 60 - int(datetime.now(timezone.utc).timestamp())) # Wait til next time + 5 mins
            leagues = await repo.GetLeagues()
            response = await client.get(f'https://www.pathofexile.com/api/currency-exchange/poe2/{current_timestamp}')
            if response.status_code != 200:
                raise Exception("GetFromApiFailure")
            
            baseCurrencies: List[str] = ['divine', 'chaos', 'exalted']

            exaltedPrice = CurrencyPrice(itemId='exalted', value=1.0, quantityTraded=1)

            data = CurrencyExchangeResponse.model_validate(response.json())
            nextFetchTime = data.next_change_id

            if (len(data.markets) == 0): # Current timestamp. Not filled in yet
                logger.error("Price history reached end. Waiting 20 mins. Shouldnt hit this.")
                await asyncio.sleep(20*60)
            
            for league in leagues:
                if (await repo.GetPricesChecked(current_timestamp, league.id)):
                    logger.info("Price already checked for this timestamp and league. continuing")
                    continue

                ### Calculate baseCurrency prices (Divine, Chaos, Exalted)
                pairs = await getLeagueData(data, league, baseCurrencies)
                chaosPairs = [pair for pair in pairs if pair.targetItem == 'chaos' and pair.baseItem == 'exalted'] # only exalted - chaos

                chaosPrice = None
                if len(chaosPairs) == 0:
                    chaosPrice = CurrencyPrice(itemId='chaos', value = await repo.GetItemPrice((await repo.GetCurrencyItem('chaos')).itemId, leagueId=league.id), quantityTraded=1)
                else:
                    for chaosPair in chaosPairs:
                        pairs.remove(chaosPair)
                        chaosPrice = CurrencyPrice(itemId='chaos', value=chaosPair.valueOfTargetItemInBaseItems, quantityTraded=chaosPair.quantityOfTargetItem)
                
                assert chaosPrice != None

                divinePairs = [pair for pair in pairs if pair.targetItem == 'divine'] # only exalted - divine and chaos - divine
                divinePrices: List[float] = []
                divineTradingQuantities = []
                for divinePair in divinePairs:
                    pairs.remove(divinePair)
                    if divinePair.baseItem == 'exalted':
                        divinePrices.append(divinePair.valueOfTargetItemInBaseItems)
                        divineTradingQuantities.append(divinePair.quantityOfTargetItem)
                    else:
                        if divinePair.baseItem != 'chaos':
                            raise Exception("Somehow got trading pair for divine that wasnt exalted or chaos")
                        divinePrices.append(divinePair.valueOfTargetItemInBaseItems * chaosPrice.value)
                        divineTradingQuantities.append(divinePair.quantityOfTargetItem)
                
                if len(divinePrices) == 0:
                    divinePrices.append(await repo.GetItemPrice((await repo.GetCurrencyItem('divine')).itemId, leagueId=league.id))
                    divineTradingQuantities.append(1)

                divinePrice = CurrencyPrice(itemId='divine', value = sum(divinePrices)/ len(divinePrices), quantityTraded=sum(divineTradingQuantities))
                
                baseItemPrices = [exaltedPrice, chaosPrice, divinePrice]

                targetItemPrices: List[CurrencyPrice] = []
                for pair in pairs:
                    targetItemPrices.append(getCurrencyPriceFromPair(pair, baseItemPrices))
                
                itemPriceMapping: Dict[str, List[CurrencyPrice]] = {}
                itemPriceMapping[divinePrice.itemId] = [divinePrice]
                itemPriceMapping[exaltedPrice.itemId] = [exaltedPrice]
                itemPriceMapping[chaosPrice.itemId] = [chaosPrice]

                for targetItemPrice in targetItemPrices:
                    if targetItemPrice.itemId not in itemPriceMapping.keys():
                        itemPriceMapping[targetItemPrice.itemId] = [targetItemPrice]
                    else:
                        itemPriceMapping[targetItemPrice.itemId].append(targetItemPrice)

                finalPrices: Dict[str, CurrencyPrice] = {}
                for key in itemPriceMapping.keys():
                    currencyPrices = itemPriceMapping[key]

                    weightedPrice = 0

                    tuples = [(cp.value, cp.quantityTraded) for cp in currencyPrices]
                    totalQuantity = sum([item[1] for item in tuples])

                    for value, quantity in tuples:
                        if totalQuantity == 0:
                            continue
                        weightedPrice += value * (quantity / totalQuantity)
                    finalPrices[key] = CurrencyPrice(itemId=key, value=weightedPrice, quantityTraded=totalQuantity)
                
                ### Record pricelogs

                currencyItems = await repo.GetCurrencyItems([key for key in finalPrices.keys()])

                itemIdLookup: Dict[str, int] = {}

                for currencyItem in currencyItems:
                    itemIdLookup[currencyItem.apiId] = currencyItem.itemId
                
                validCurrencyItemApiIds = set(itemIdLookup.keys())
                for key, value in finalPrices.items():
                    if key not in validCurrencyItemApiIds:
                        finalPrices.pop(key)
                
                priceLogs = [RecordPriceModel(itemId=itemIdLookup[value.itemId], leagueId=league.id, price=value.value, quantity=value.quantityTraded) for value in finalPrices.values()]
                await repo.RecordPriceBulk(priceLogs, current_timestamp)
            current_timestamp = nextFetchTime

def getCurrencyPriceFromPair(pair: LeagueCurrencyPairData, baseItemPrices: List[CurrencyPrice]) -> CurrencyPrice:
    for baseItemPrice in baseItemPrices:
        if pair.baseItem != baseItemPrice.itemId:
            continue

        return CurrencyPrice(itemId=pair.targetItem, value=pair.valueOfTargetItemInBaseItems * baseItemPrice.value, quantityTraded=pair.quantityOfTargetItem)
    else:
        raise Exception("Somehow didnt find baseItemPrice for a pairs baseItem")
            
async def getLeagueData(data: CurrencyExchangeResponse, league: League, baseItems: List[str]) -> List[LeagueCurrencyPairData]:
    pairs: List[LeagueCurrencyPairData] = []
    currentLeagueMarkets = [pair for pair in data.markets if pair.league == league.value]
    for listing in currentLeagueMarkets:
        item1, item2 = listing.market_id.split('|')

        # No important baseCurrency in pair.
        if not (item1 in baseItems or item2 in baseItems):
            continue

        if (listing.volume_traded[item1] == 0):
            continue

        # Pair is 2 important baseCurrencies
        # Create a pair for each side
        # else
        # just create a pair with exalted as the base
        if (item1 in baseItems and item2 in baseItems):
            if item1 != 'exalted' and item2 != 'exalted':
                if item1 == 'chaos':
                    baseItem = item1 
                    targetItem = item2 
                else:
                    baseItem = item2 
                    targetItem = item1 
            elif (item1 == 'exalted'):
                baseItem = item1 
                targetItem = item2 
            else:
                baseItem = item2 
                targetItem = item1
        elif item1 in baseItems:
            baseItem = item1 
            targetItem = item2 
        else:
            baseItem = item2
            targetItem = item1

        valueOfTarget = listing.volume_traded[baseItem] / listing.volume_traded[targetItem]  # 1 / 300 # 0.0033 value of target item in divines.
        quantityOfPairTraded = listing.volume_traded[targetItem] # 300. How many people actually traded in this item for that.
        pairs.append(LeagueCurrencyPairData(league=league, baseItem=baseItem, targetItem=targetItem, valueOfTargetItemInBaseItems=valueOfTarget, quantityOfTargetItem=quantityOfPairTraded))

    return pairs

async def FetchPrices(repo: ItemRepository):

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

            logger.info(f"fetching {len(uniqueItems)} unique items")
                        
            if len(itemIdsToFetch) == 0:
                logger.info(f"No items to fetch")
                continue
                
            divinePrice = await repo.GetItemPrice(divineItem.itemId, league.id)

            await process_uniques(uniqueItems, league, repo, client, exaltedItem, divineItem, divinePrice)
           
            currencyItems = [item for item in baseCurrencyItems if item.itemId in itemIdsToFetch]
            for currencyItem in currencyItems:
                if currencyItem.itemMetadata is None:
                    logger.info(f"Syncing metadata and icon for {currencyItem.text}")
                    await sync_metadata_and_icon(currencyItem, repo, client, BASE_URL, REALM, leagues[0].value)



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
            
async def process_base_items(baseItems: list[UniqueBaseItem], league: League, repo: ItemRepository, client: PoeTradeClient):
    for baseItem in baseItems:
        logger.info(f"Fetching price for {baseItem.name} in {league.value}")
        price_result = await fetch_base(baseItem, league, repo, client)
        logger.info(f"Price: {price_result.price}, quantity: {price_result.quantity}")
        await record_price(price_result.price, baseItem.itemId, league.id, price_result.quantity, repo)