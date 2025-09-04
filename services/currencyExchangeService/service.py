import asyncio
from datetime import datetime, timezone
from decimal import Decimal
import logging
from typing import List, Optional

from pydantic import BaseModel
from services.currencyExchangeService.config import CurrencyExchangeServiceConfig
from services.libs.models.CurrencyExchange.models import CurrencyExchangeSnapshot, CurrencyExchangeSnapshotPair, CurrencyExchangeSnapshotPairData
from services.libs.models.CurrencyExchangeResponse import CurrencyExchangeResponse, TradingPair
from services.repositories.currency_exchange_repository import CurrencyExchangeRepository
from services.repositories.item_repository import ItemRepository
from services.libs.poe_trade_client import PoeApiClient
from services.repositories.item_repository.GetAllCurrencyItems import CurrencyItem
from services.repositories.item_repository.GetItemPricesInRange import GetItemPricesInRangeModel
logger = logging.getLogger(__name__)



async def run(config: CurrencyExchangeServiceConfig, itemRepo: ItemRepository, cxRepo: CurrencyExchangeRepository, client: PoeApiClient):
    CurrentEpochUtc = int(datetime.now(tz=timezone.utc).timestamp())
    LastFetchedEpochUtc = (await cxRepo.GetLastFetchedEpoch()).Epoch
    TimeToFetchUtc = LastFetchedEpochUtc + 60 * 60 if LastFetchedEpochUtc is not None else None

    if TimeToFetchUtc:
        logger.info(f"{TimeToFetchUtc}")
        await asyncio.sleep(TimeToFetchUtc + 60 * 5 - CurrentEpochUtc)

    if TimeToFetchUtc is None:
        url = 'https://www.pathofexile.com/api/currency-exchange/poe2'
    else:
        url = f'https://www.pathofexile.com/api/currency-exchange/poe2/{TimeToFetchUtc}'

    response = await client.get(url)

    if response.status_code != 200:
        raise Exception("GetFromApiFailure")
    print(TimeToFetchUtc)
    data = CurrencyExchangeResponse.model_validate(response.json())

    print(datetime.fromtimestamp(data.next_change_id))
    fetchStatus = await itemRepo.GetCurrencyFetchStatus(startTime=datetime.fromtimestamp(data.next_change_id))

    if fetchStatus == False:
        logger.info("Prices not fetched yet")
        return
    
    leagues = await itemRepo.GetAllLeagues()

    currencies = await itemRepo.GetAllCurrencyItems()

    currencyLookupByApiId = {currency.apiId: currency for currency in currencies}

    leagueToPricesLookup: dict[int, List[GetItemPricesInRangeModel]] = {}

    for league in leagues:
        itemPrices = await itemRepo.GetItemPricesInRange(
            itemIds= [item.itemId for item in currencies],
            leagueId= league.id,
            startTime= datetime.fromtimestamp(data.next_change_id - 60 * 60),
            endTime= datetime.fromtimestamp(data.next_change_id))
        print(itemPrices)
        leagueToPricesLookup[league.id] = itemPrices

    leaguesToFetch = [league for league in leagues if league.id in leagueToPricesLookup.keys()]

    logger.info(f"leagues to fetch {leaguesToFetch}")
    for league in leaguesToFetch:
        logger.info(f"analyzing league {league}")

        itemPriceLookupByItemId = {item.ItemId: item for item in leagueToPricesLookup[league.id]}
        
        pairs = [pair for pair in data.markets if pair.league == league.value]

        snapshot = CurrencyExchangeSnapshot(Epoch = data.next_change_id - 60 * 60, 
                                            LeagueId=league.id, 
                                            Pairs=[])
        
        presentApiIds = currencyLookupByApiId.keys()
        for pair in pairs:
            pairCurrencies = pair.market_id.split("|")
            if pairCurrencies[0] not in presentApiIds or pairCurrencies[1] not in presentApiIds:
                logger.error(f"One of the currencies in {pairCurrencies} is not present in db. Skipping pair")
                continue
                
            currencyOne = currencyLookupByApiId[pairCurrencies[0]]
            currencyTwo = currencyLookupByApiId[pairCurrencies[1]]

            currencyOneData = GetPairData(currencyOne, itemPriceLookupByItemId, pair, currencyTwo)
            currencyTwoData = GetPairData(currencyTwo, itemPriceLookupByItemId, pair, currencyOne)

            mostLiquidCurrency = currencyOneData if itemPriceLookupByItemId[currencyOne.itemId].Quantity > itemPriceLookupByItemId[currencyTwo.itemId].Quantity else currencyTwoData
            
            snapshotPair = CurrencyExchangeSnapshotPair(
                CurrencyOneItemId= currencyOne.itemId,
                CurrencyTwoItemId= currencyTwo.itemId,
                Volume= mostLiquidCurrency.ValueTraded,
                CurrencyOneData= currencyOneData,
                CurrencyTwoData= currencyTwoData
            )
            
            snapshot.Pairs.append(snapshotPair)
        
        Volume = 0
        MarketCap = 0
        for pair in snapshot.Pairs:
            Volume += pair.Volume
            MarketCap += pair.CurrencyOneData.StockValue
            MarketCap += pair.CurrencyTwoData.StockValue
        
        snapshot.Volume = Decimal(Volume)
        snapshot.MarketCap = Decimal(MarketCap)

        logger.info(f"Saving {len(snapshot.Pairs)} for {snapshot.LeagueId}")
        await cxRepo.CreateSnapshot(snapshot)

def GetPairData(CurrencyItem: CurrencyItem, itemPriceLookup: dict[int, GetItemPricesInRangeModel], pair: TradingPair, otherCurrencyItem: CurrencyItem) -> CurrencyExchangeSnapshotPairData:
    volumeTraded = pair.volume_traded[CurrencyItem.apiId]
    valueTraded = volumeTraded * itemPriceLookup[CurrencyItem.itemId].Price
    if volumeTraded != 0:
        relativePrice = Decimal(pair.volume_traded[otherCurrencyItem.apiId] / volumeTraded) * itemPriceLookup[otherCurrencyItem.itemId].Price
    else: 
        relativePrice = Decimal(0)
    highestStock = pair.highest_stock[CurrencyItem.apiId]

    return CurrencyExchangeSnapshotPairData(
        VolumeTraded= volumeTraded,
        ValueTraded= valueTraded,
        RelativePrice= relativePrice,
        HighestStock= highestStock,
        StockValue= highestStock * itemPriceLookup[CurrencyItem.itemId].Price
        )