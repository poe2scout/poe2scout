from fastapi import APIRouter, Depends
from src.services.apiService.dependancies import get_item_repository
from src.services.repositories import ItemRepository
from pydantic import BaseModel

from src.services.repositories.item_repository.GetSnapshotForLeague import LeagueSnapshot

router = APIRouter(prefix="/dbDumps")


class LeagueSnapshotModel(BaseModel):
    leagueId: int
    priceLogs: list[LeagueSnapshot]


class GetSnapshotResponse(BaseModel):
    snapshots: list[LeagueSnapshotModel] = []


@router.get("/GetSnapshot")
async def GetSnapshot(
    repo: ItemRepository = Depends(get_item_repository),
) -> GetSnapshotResponse:
    leagues = await repo.GetLeagues()

    response: GetSnapshotResponse = GetSnapshotResponse()

    for league in leagues:
        response.snapshots.append(
            LeagueSnapshotModel(
                leagueId=league.id, priceLogs=await repo.GetSnapshotForLeague(league.id)
            )
        )

    return response
