from .CreateBaseItem import CreateBaseItem
from .GetAllBaseItems import GetAllBaseItems
from .CreateCurrencyCategory import CreateCurrencyCategory
from .GetAllCurrencyCategories import GetAllCurrencyCategories
from .CreateCurrencyItem import CreateCurrencyItem
from .GetAllCurrencyItems import GetAllCurrencyItems
from .CreateItemCategory import CreateItemCategory
from .GetAllItemCategories import GetAllItemCategories
from .CreateItemType import CreateItemType
from .GetAllItemTypes import GetAllItemTypes
from .CreateUniqueItem import CreateUniqueItem
from .GetAllUniqueItems import GetAllUniqueItems
from .CreateItem import CreateItem
from .GetAllItems import GetAllItems
from .RecordPrice import RecordPrice
from .GetCurrencyItem import GetCurrencyItem
from .GetLeagues import GetLeagues
from .GetItemPrice import GetItemPrice
from .GetUniqueItemsByCategory import GetUniqueItemsByCategory
from .GetCurrencyItemsByCategory import GetCurrencyItemsByCategory
from .GetItemPriceLogs import GetItemPriceLogs
from .GetLeagueByValue import GetLeagueByValue
from .GetSearchOptions import GetSearchOptions
from .OverwriteCategory import OverwriteCategory
from .SetUniqueItemMetadata import SetUniqueItemMetadata
from .UpdateUniqueIconUrl import UpdateUniqueIconUrl
from .SetCurrencyItemMetadata import SetCurrencyItemMetadata
from .UpdateCurrencyIconUrl import UpdateCurrencyIconUrl
from .GetFetchedItemIds import GetFetchedItemIds
from .GetItemPriceHistory import GetItemPriceHistory
from .GetCurrencyItems import GetCurrencyItems

class ItemRepository:
    def __init__(self):
        self.CreateBaseItem = CreateBaseItem().execute
        self.GetAllBaseItems = GetAllBaseItems().execute
        self.CreateCurrencyCategory = CreateCurrencyCategory().execute
        self.GetAllCurrencyCategories = GetAllCurrencyCategories().execute
        self.CreateCurrencyItem = CreateCurrencyItem().execute
        self.GetAllCurrencyItems = GetAllCurrencyItems().execute
        self.CreateItemCategory = CreateItemCategory().execute
        self.GetAllItemCategories = GetAllItemCategories().execute
        self.CreateItemType = CreateItemType().execute
        self.GetAllItemTypes = GetAllItemTypes().execute
        self.CreateUniqueItem = CreateUniqueItem().execute
        self.GetAllUniqueItems = GetAllUniqueItems().execute
        self.CreateItem = CreateItem().execute
        self.GetAllItems = GetAllItems().execute
        self.RecordPrice = RecordPrice().execute
        self.GetCurrencyItem = GetCurrencyItem().execute
        self.GetLeagues = GetLeagues().execute
        self.GetItemPrice = GetItemPrice().execute  
        self.GetUniqueItemsByCategory = GetUniqueItemsByCategory().execute
        self.GetCurrencyItemsByCategory = GetCurrencyItemsByCategory().execute
        self.GetItemPriceLogs = GetItemPriceLogs().execute
        self.GetLeagueByValue = GetLeagueByValue().execute
        self.GetSearchOptions = GetSearchOptions().execute
        self.OverwriteCategory = OverwriteCategory().execute
        self.SetUniqueItemMetadata = SetUniqueItemMetadata().execute
        self.UpdateUniqueIconUrl = UpdateUniqueIconUrl().execute
        self.SetCurrencyItemMetadata = SetCurrencyItemMetadata().execute
        self.UpdateCurrencyIconUrl = UpdateCurrencyIconUrl().execute
        self.GetFetchedItemIds = GetFetchedItemIds().execute
        self.GetItemPriceHistory = GetItemPriceHistory().execute    
        self.GetCurrencyItems = GetCurrencyItems().execute