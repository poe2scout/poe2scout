
from datetime import datetime
from typing import List

from fastapi import Depends, HTTPException
from pydantic import BaseModel

from services.apiService.dependancies import ItemRepoDep
from services.repositories.item_repository import ItemRepository
from . import router


@router.get("/ItemHistories")
async def GetAllItemHistories(league: str, repo: ItemRepoDep):
    leagueInDb = await repo.GetLeagueByValue(league)
    if not leagueInDb:
        raise HTTPException(400, "Invalid league name")
    
    return await repo.GetAllItemHistories(leagueInDb.id)
