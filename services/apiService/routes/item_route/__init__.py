from fastapi import APIRouter
from .GetCategories import router as categories_router
from .GetUniqueItems import GetUniqueItems as unique_items_router
from .GetCurrencyItems import GetCurrencyItems as currency
from .GetFilters import GetFilters
from .GetAllItems import GetAllItems
from .GetHistory import GetHistory
from .GetLandingSplashInfo import GetLandingSplashInfo
from .GetCurrencyItemById import GetCurrencyItemById


router = APIRouter(prefix="/items", tags=["items"])


