import sys
from typing import Dict, List
from pydantic import BaseModel
from services.libs.models.CurrencyExchangeResponse import (
    CurrencyExchangeResponse,
    LeagueCurrencyPairData,
)
from services.repositories.currency_exchange_repository import (
    CurrencyExchangeRepository,
)
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


async def run(
    config: PriceFetchConfig, repo: ItemRepository, cxRepo: CurrencyExchangeRepository
):
    # Define the schedule

    logger.info("Price fetch service started.")
    await asyncio.gather(
        runCurrencyExchangePrices(repo, config, cxRepo), FetchPrices(repo)
    )


async def runCurrencyExchangePrices(
    repo: ItemRepository, config: PriceFetchConfig, cxRepo: CurrencyExchangeRepository
):
    headers = {"User-Agent": "POE2SCOUT (contact: b@girardet.co.nz)"}
    async with PoeApiClient(
        config.POEAPI_CLIENT_ID, config.POEAPI_CLIENT_SECRET, headers=headers
    ) as client:
        while True:
            await FetchCurrencyExchangePrices(repo, config, cxRepo, client)
            await asyncio.sleep(10)


class CurrencyPrice(BaseModel):
    itemId: str
    value: float  # In exalts
    quantityTraded: int


async def FetchCurrencyExchangePrices(
    repo: ItemRepository,
    config: PriceFetchConfig,
    cxRepo: CurrencyExchangeRepository,
    client: PoeApiClient,
):
    lastFetchEpoch = (await cxRepo.GetServiceCacheValue("PriceFetch_Currency")).Value
    currentEpoch = lastFetchEpoch + 60 * 60

    logger.info("Checking for currencies")

    await asyncio.sleep(
        currentEpoch + 61 * 60 - int(datetime.now(timezone.utc).timestamp())
    )  # Wait til next time
    leagues = await repo.GetAllLeagues()

    url = f"https://www.pathofexile.com/api/currency-exchange/poe2/{currentEpoch}"

    response = await client.get(url)
    if response.status_code != 200:
        logger.error(response.json())
        raise Exception("GetFromApiFailure")

    baseCurrencies: List[str] = ["divine", "chaos", "exalted"]

    exaltedPrice = CurrencyPrice(itemId="exalted", value=1.0, quantityTraded=1)

    data = CurrencyExchangeResponse.model_validate(response.json())

    if data.next_change_id == currentEpoch:
        logger.error("Reached the end. Somethings gone wrong.")
        await asyncio.sleep(60 * 10)

        return

    if len(data.markets) == 0:  # Current timestamp. Not filled in yet
        logger.info("No pairs in markets.")
        await cxRepo.SetServiceCacheValue("PriceFetch_Currency", currentEpoch)
        return
    logger.info("Updating correctly")
    try:
        for league in leagues:
            if await repo.GetPricesChecked(currentEpoch, league.id):
                logger.info(
                    "Price already checked for this timestamp and league. continuing"
                )
                continue

            ### Calculate baseCurrency prices (Divine, Chaos, Exalted)
            pairs = await getLeagueData(data, league, baseCurrencies)
            chaosPairs = [
                pair
                for pair in pairs
                if pair.targetItem == "chaos" and pair.baseItem == "exalted"
            ]  # only exalted - chaos

            chaosPrice = None
            if len(chaosPairs) == 0:
                logger.info("No chaos pair")
                itemPrice = await repo.GetItemPrice(
                    (await repo.GetCurrencyItem("chaos")).itemId, league.id, currentEpoch
                )
                if itemPrice == 0:
                    current_timestamp = data.next_change_id
                    continue

                chaosPrice = CurrencyPrice(
                    itemId="chaos", value=itemPrice, quantityTraded=0
                )
            else:
                for chaosPair in chaosPairs:
                    pairs.remove(chaosPair)
                    chaosPrice = CurrencyPrice(
                        itemId="chaos",
                        value=chaosPair.valueOfTargetItemInBaseItems,
                        quantityTraded=chaosPair.quantityOfTargetItem,
                    )

            assert chaosPrice != None

            divinePairs = [
                pair for pair in pairs if pair.targetItem == "divine"
            ]  # only exalted - divine and chaos - divine
            divinePrices: List[float] = []
            divineTradingQuantities = []
            for divinePair in divinePairs:
                pairs.remove(divinePair)
                if divinePair.baseItem == "exalted":
                    divinePrices.append(divinePair.valueOfTargetItemInBaseItems)
                    divineTradingQuantities.append(divinePair.quantityOfTargetItem)
                else:
                    if divinePair.baseItem != "chaos":
                        raise Exception(
                            "Somehow got trading pair for divine that wasnt exalted or chaos"
                        )
                    divinePrices.append(
                        divinePair.valueOfTargetItemInBaseItems * chaosPrice.value
                    )
                    divineTradingQuantities.append(divinePair.quantityOfTargetItem)

            if len(divinePrices) == 0:
                logger.info("No divine pair")
                itemPrice = await repo.GetItemPrice(
                    (await repo.GetCurrencyItem("divine")).itemId, league.id, currentEpoch
                )
                if itemPrice == 0:
                    current_timestamp = data.next_change_id
                    continue

                divinePrices.append(itemPrice)

            divinePrice = CurrencyPrice(
                itemId="divine",
                value=sum(divinePrices) / len(divinePrices),
                quantityTraded=sum(divineTradingQuantities),
            )

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
                finalPrices[key] = CurrencyPrice(
                    itemId=key, value=weightedPrice, quantityTraded=totalQuantity
                )

            ### Record pricelogs

            currencyItems = await repo.GetCurrencyItems([key for key in finalPrices.keys()])

            itemIdLookup: Dict[str, int] = {}

            for currencyItem in currencyItems:
                itemIdLookup[currencyItem.apiId] = currencyItem.itemId

            validCurrencyItemApiIds = set(itemIdLookup.keys())
            for key, value in finalPrices.items():
                if key not in validCurrencyItemApiIds:
                    finalPrices.pop(key)

            priceLogs = [
                RecordPriceModel(
                    itemId=itemIdLookup[value.itemId],
                    leagueId=league.id,
                    price=value.value,
                    quantity=value.quantityTraded,
                )
                for value in finalPrices.values()
                if value.value != 0
            ]

            if len(priceLogs) == 1 and priceLogs[0].itemId == exaltedPrice.itemId:
                logger.info("Only price is exalted. Skipping save.")
            else:
                logger.info(
                    f"Saving {len(priceLogs)} logs for {league.value} at {currentEpoch} or more specifically {datetime.fromtimestamp(currentEpoch)}"
                )
                await repo.RecordPriceBulk(priceLogs, currentEpoch)
    except Exception as e:
    # Catches any other unexpected exceptions
        logger.info(f"An unexpected error occurred: {e}")

    logger.info(
                f"Saving cache value. {currentEpoch}"
            )
    await cxRepo.SetServiceCacheValue("PriceFetch_Currency", currentEpoch)


def getCurrencyPriceFromPair(
    pair: LeagueCurrencyPairData, baseItemPrices: List[CurrencyPrice]
) -> CurrencyPrice:
    for baseItemPrice in baseItemPrices:
        if pair.baseItem != baseItemPrice.itemId:
            continue

        return CurrencyPrice(
            itemId=pair.targetItem,
            value=pair.valueOfTargetItemInBaseItems * baseItemPrice.value,
            quantityTraded=pair.quantityOfTargetItem,
        )
    else:
        raise Exception("Somehow didnt find baseItemPrice for a pairs baseItem")


async def getLeagueData(
    data: CurrencyExchangeResponse, league: League, baseItems: List[str]
) -> List[LeagueCurrencyPairData]:
    pairs: List[LeagueCurrencyPairData] = []
    currentLeagueMarkets = [
        pair for pair in data.markets if pair.league == league.value
    ]
    for listing in currentLeagueMarkets:
        item1, item2 = listing.market_id.split("|")

        # No important baseCurrency in pair.
        if not (item1 in baseItems or item2 in baseItems):
            continue

        if listing.volume_traded[item1] == 0:
            continue

        # Pair is 2 important baseCurrencies
        # Create a pair for each side
        # else
        # just create a pair with exalted as the base
        if item1 in baseItems and item2 in baseItems:
            if item1 != "exalted" and item2 != "exalted":
                if item1 == "chaos":
                    baseItem = item1
                    targetItem = item2
                else:
                    baseItem = item2
                    targetItem = item1
            elif item1 == "exalted":
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

        valueOfTarget = (
            listing.volume_traded[baseItem] / listing.volume_traded[targetItem]
        )  # 1 / 300 # 0.0033 value of target item in divines.
        quantityOfPairTraded = listing.volume_traded[
            targetItem
        ]  # 300. How many people actually traded in this item for that.
        pairs.append(
            LeagueCurrencyPairData(
                league=league,
                baseItem=baseItem,
                targetItem=targetItem,
                valueOfTargetItemInBaseItems=valueOfTarget,
                quantityOfTargetItem=quantityOfPairTraded,
            )
        )

    return pairs


async def FetchPrices(repo: ItemRepository):
    headers = {"User-Agent": "POE2SCOUT (contact: b@girardet.co.nz)"}
    async with PoeTradeClient(headers=headers) as client:
        while True:
            # Get all unqiue items
            leagues = await repo.GetLeagues()
            leagues = [league for league in leagues if league.id == 7] # Fate of the Vaal
            baseUniqueItems = await repo.GetAllUniqueItems()
            baseCurrencyItems = await repo.GetAllCurrencyItems()

            exaltedItem = await repo.GetCurrencyItem("exalted")
            divineItem = await repo.GetCurrencyItem("divine")

            for league in leagues:
                current_time = datetime.now().strftime("%H")
                fetchedItemIds: list[int] = await repo.GetFetchedItemIds(
                    current_time, league.id
                )
                itemIds = await repo.GetAllItems()
                itemIds = [item.id for item in itemIds if item.id not in fetchedItemIds]

                itemIdsToFetch = [
                    item for item in itemIds if item not in fetchedItemIds
                ]

                uniqueItems = [
                    item for item in baseUniqueItems if item.itemId in itemIdsToFetch
                ]

                logger.info(f"fetching {len(uniqueItems)} unique items")

                if len(itemIdsToFetch) == 0:
                    logger.info("No items to fetch")
                    continue

                divinePrice = await repo.GetItemPrice(divineItem.itemId, league.id)

                await process_uniques(
                    uniqueItems,
                    league,
                    repo,
                    client,
                    exaltedItem,
                    divineItem,
                    divinePrice,
                )

                currencyItems = [item for item in baseCurrencyItems]
                for currencyItem in currencyItems:
                    if currencyItem.itemMetadata is None:
                        logger.info(
                            f"Syncing metadata and icon for {currencyItem.text}"
                        )
                        await sync_metadata_and_icon(
                            currencyItem,
                            repo,
                            client,
                            BASE_URL,
                            REALM,
                            leagues[0].value,
                        )


BASE_URL = "https://www.pathofexile.com/api/trade2"
REALM = "poe2"


async def process_uniques(
    uniqueItems: list[UniqueItem],
    league: League,
    repo: ItemRepository,
    client: PoeTradeClient,
    exaltedItem: CurrencyItem,
    divineItem: CurrencyItem,
    divinePrice: float,
):
    for uniqueItem in uniqueItems:
        try:
            ### Fetch price of exalt, chaos, div
            ### Use price with highest quantity as the actual price
            ### Gotten rid of all anti price fixing.
            ### After the league has progressed half a day? Turn on instant buy out only.
            logger.info(f"Fetching price for {uniqueItem.name} in {league.value}")
            exaltPriceFetchResult: PriceFetchResult = await fetch_unique(
                uniqueItem, league, repo, client, "exalted"
            )
            chaosPriceFetchResult: PriceFetchResult = await fetch_unique(
                uniqueItem, league, repo, client, "chaos"
            )
            divinePriceFetchResult: PriceFetchResult = await fetch_unique(
                uniqueItem, league, repo, client, "divine"
            )
            logger.info(f"Exalt price info: {exaltPriceFetchResult}")

            prices: List[PriceFetchResult] = [
                exaltPriceFetchResult,
                chaosPriceFetchResult,
                divinePriceFetchResult,
            ]
            prices = [price for price in prices if price.price > 0]

            if len(prices) == 0:
                logger.info(f"No valid priceFetchResults for {uniqueItem}")
                continue

            lowest_price = sys.maxsize
            quantity = 0
            for price in prices:
                currency = await repo.GetCurrencyItem(price.currency)
                currencyPrice = await repo.GetItemPrice(currency.itemId, league.id)

                item_price = price.price * currencyPrice
                quantity += price.quantity
                if item_price < lowest_price:
                    lowest_price = item_price

            logger.info(
                f"Recording price for {uniqueItem.name} in {league.value} with price {lowest_price} and quantity {quantity}"
            )
            await record_price(
                lowest_price, uniqueItem.itemId, league.id, quantity, repo
            )
        except:
            logger.error(f"error fetching for {uniqueItem}")
