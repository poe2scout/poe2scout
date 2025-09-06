
from datetime import datetime, timedelta
import logging
import random
from typing import Generic, List, TypeVar

from pydantic import BaseModel
from services.libs.models.PaginationParams import PaginationParams 
from services.repositories.item_repository import ItemRepository
from services.repositories.models import CurrencyItemExtended, UniqueItemExtended

T = TypeVar('T')

logger = logging.getLogger(__name__)

class CacheState(Generic[T], BaseModel):
    Value: List[T]
    Expires: datetime

class CacheKey(BaseModel):
    Category: str
    LeagueId: int

    class Config:
        frozen = True

class EconomyCache:
    CurrencyCache: dict[CacheKey, CacheState[CurrencyItemExtended]]
    UniqueCache: dict[CacheKey, CacheState[UniqueItemExtended]]

    repo: ItemRepository

    def __init__(self, repo: ItemRepository):
        self.CurrencyCache = {}
        self.UniqueCache = {}
        self.repo = repo

    async def GetCurrencyPage(self, leagueId: int, category: str, search: str) -> List[CurrencyItemExtended]:
        items: List[CurrencyItemExtended]

        cacheKey = CacheKey(Category=category, LeagueId=leagueId)
        if self.CurrencyCache.get(cacheKey) is not None and self.CurrencyCache[cacheKey].Expires > datetime.now():
            logger.info(f"HitCache for {cacheKey}")
            items = self.CurrencyCache[cacheKey].Value
        else:
            logger.info(f"Cache empty for {cacheKey}")
            items = await self.FetchCurrencyPage(cacheKey)
        
        if search != "":
            items = [item for item in items if item.text == search]
        
        return items
    
    async def GetUniquePage(self, leagueId: int, category: str, search: str) -> List[UniqueItemExtended]:
        items: List[UniqueItemExtended]

        cacheKey = CacheKey(Category=category, LeagueId=leagueId)
        if self.UniqueCache.get(cacheKey) is not None and self.UniqueCache[cacheKey].Expires > datetime.now():
            logger.info(f"HitCache for {cacheKey}")
            items = self.UniqueCache[cacheKey].Value
        else:
            logger.info(f"Cache empty for {cacheKey}")
            items = await self.FetchUniquePage(cacheKey)
        if search != "":
            items = [item for item in items if item.name.lower() == search.lower()]
        
        return items
    
    async def FetchUniquePage(self, cacheKey: CacheKey) -> List[UniqueItemExtended]:    
        uniqueItems = await self.repo.GetUniqueItemsByCategory(cacheKey.Category)

        itemsInCurrentLeague = await self.repo.GetItemsInCurrentLeague(cacheKey.LeagueId)

        uniqueItems = [uniqueItem for uniqueItem in uniqueItems if uniqueItem.itemId in itemsInCurrentLeague]
        itemIds = [item.itemId for item in uniqueItems]

        priceLogs = await self.repo.GetItemPriceLogs(itemIds, cacheKey.LeagueId)

        items = [UniqueItemExtended(
            **item.model_dump(), priceLogs=priceLogs[item.itemId]) for item in uniqueItems]

        itemCount = len(items)
        lastPrice = dict.fromkeys(itemIds, 0)

        for item in items:
            for log in item.priceLogs:
                if log and hasattr(log, 'price'):
                    lastPrice[item.itemId] = log.price
                    break


        items.sort(
            key=lambda item: (
                lastPrice[item.itemId]
                if item.itemId in lastPrice
                else 0
            ),
            reverse=True
        )


        items = [UniqueItemExtended(
            **item.model_dump(exclude={'currentPrice'}), currentPrice=lastPrice[item.itemId]) for item in items]
        
        self.UniqueCache[cacheKey] = CacheState[UniqueItemExtended](Value=items, Expires=datetime.now()+ timedelta(hours=1, minutes=random.randint(0, 15)))

        return items
    


    
    async def FetchCurrencyPage(self, cacheKey: CacheKey) -> List[CurrencyItemExtended]:
        itemsInCurrentLeague = await self.repo.GetItemsInCurrentLeague(cacheKey.LeagueId)
        currencyItems = await self.repo.GetCurrencyItemsByCategory(cacheKey.Category)
        currencyItems = [currencyItem for currencyItem in currencyItems if currencyItem.itemId in itemsInCurrentLeague]
        itemIds = [item.itemId for item in currencyItems]
        
        priceLogs = await self.repo.GetItemPriceLogs(itemIds, cacheKey.LeagueId)
        items = [CurrencyItemExtended(
            **item.model_dump(), priceLogs=priceLogs[item.itemId]) for item in currencyItems]


        lastPrice = dict.fromkeys(itemIds, 0.0)

        prices = await self.repo.GetItemPrices(itemIds, cacheKey.LeagueId)

        pricesLookup = {price.ItemId: price for price in prices}

        for item in items:
            lastPrice[item.itemId] = pricesLookup[item.itemId].Price

        items.sort(
            key=lambda item: (
                lastPrice[item.itemId]
                if item.itemId in lastPrice
                else 0
            ),
            reverse=True
        )

        items = [CurrencyItemExtended(
            **item.model_dump(exclude={'currentPrice'}), currentPrice=lastPrice[item.itemId]) for item in items]
        
        self.CurrencyCache[cacheKey] = CacheState[CurrencyItemExtended](Value=items, Expires=datetime.now()+ timedelta(hours=1, minutes=random.randint(0, 15)))

        return items

        