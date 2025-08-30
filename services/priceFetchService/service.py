from typing import Dict, List
from pydantic import BaseModel
from services.priceFetchService.models.CurrencyExchangeResponse import CurrencyExchangeResponse, LeagueCurrencyPairData
from services.repositories.item_repository import ItemRepository
from services.repositories.item_repository.RecordPrice import RecordPriceModel
from .functions.fetch_unique import PriceFetchResult, fetch_unique
from .functions.record_price import record_price
import logging
from .config import PriceFetchConfig
from .functions.sync_metadata_and_icon import sync_metadata_and_icon
from datetime import datetime, timezone
from services.libs.poe_trade_client import PoeApiClient, PoeTradeClient
from services.repositories.item_repository.GetAllUniqueItems import UniqueItem
from services.repositories.item_repository.GetAllCurrencyItems import CurrencyItem
from services.repositories.item_repository.GetLeagues import League

import asyncio
logger = logging.getLogger(__name__)

async def run(config: PriceFetchConfig, repo: ItemRepository):
    # Define the schedule

    logger.info(f"Price fetch service started.")
    await asyncio.gather(FetchCurrencyExchangePrices(repo, config),
                        FetchPrices(repo))


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
            await asyncio.sleep(current_timestamp + 60 * 60 - int(datetime.now(timezone.utc).timestamp())) # Wait til next time
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
    headers = {
        "User-Agent": "POE2SCOUT (contact: b@girardet.co.nz)"
    }
    async with PoeTradeClient(headers=headers) as client:
        while True:
            # Get all unqiue items
            leagues = await repo.GetLeagues()
            leagues = [league for league in leagues if league.id == 3]
            baseUniqueItems = await repo.GetAllUniqueItems()
            baseCurrencyItems = await repo.GetAllCurrencyItems()

            exaltedItem = await repo.GetCurrencyItem("exalted")
            divineItem = await repo.GetCurrencyItem("divine")

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
        try:
            ### Fetch price of exalt, chaos, div
            ### Use price with highest quantity as the actual price
            ### Gotten rid of all anti price fixing. 
            ### After the league has progressed half a day? Turn on instant buy out only.
            logger.info(f"Fetching price for {uniqueItem.name} in {league.value}")
            exaltPriceFetchResult: PriceFetchResult = await fetch_unique(uniqueItem, 
                                                                    league, 
                                                                    repo, 
                                                                    client,
                                                                    'exalted')
            chaosPriceFetchResult: PriceFetchResult = await fetch_unique(uniqueItem, 
                                                                    league, 
                                                                    repo, 
                                                                    client,
                                                                    'chaos')
            divinePriceFetchResult: PriceFetchResult = await fetch_unique(uniqueItem, 
                                                                    league, 
                                                                    repo, 
                                                                    client,
                                                                    'divine')
            logger.info(f"Exalt price info: {exaltPriceFetchResult}")

            prices: List[PriceFetchResult] = [exaltPriceFetchResult, chaosPriceFetchResult, divinePriceFetchResult]
            prices = [price for price in prices if price.price > 0]

            if len(prices) == 0:
                logger.info(f"No valid priceFetchResults for {uniqueItem}")
                continue

            sortedPrice = sorted(prices, key=lambda price: price.quantity, reverse=True)

            mostListedResult = sortedPrice[0]

            currency = await repo.GetCurrencyItem(mostListedResult.currency)
            currencyPrice = await repo.GetItemPrice(currency.itemId, league.id)

            (price, quantity) = (mostListedResult.price * currencyPrice, mostListedResult.quantity)
            logger.info(f"Recording price for {uniqueItem.name} in {league.value} with price {price} and quantity {quantity}")
            await record_price(price, uniqueItem.itemId, league.id, quantity, repo)
        except:
            logger.error(f"error fetching for {uniqueItem}")