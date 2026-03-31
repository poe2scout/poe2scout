from . import router
from fastapi import Depends
from poe2scout.api.dependancies import get_item_repository
from poe2scout.db.repositories import ItemRepository


@router.get("/filters")
async def GetFilters(item_repository: ItemRepository = Depends(get_item_repository)):
    filters = await item_repository.GetSearchOptions()

    return filters
