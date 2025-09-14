
from fastapi import HTTPException

from services.apiService.dependancies import ItemRepoDep
from . import router


@router.get("/ItemHistories")
async def GetAllItemHistories(league: str, repo: ItemRepoDep):
    leagueInDb = await repo.GetLeagueByValue(league)
    if not leagueInDb:
        raise HTTPException(400, "Invalid league name")

    return await repo.GetAllItemHistories(leagueInDb.id)
