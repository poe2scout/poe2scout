from . import router
from fastapi import Depends
from src.services.apiService.dependancies import get_item_repository
from src.services.repositories import ItemRepository


@router.get("/filters")
async def GetFilters(item_repository: ItemRepository = Depends(get_item_repository)):
    filters = await item_repository.GetSearchOptions()

    return filters
