import io
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from services.apiService.dependancies import get_item_repository
from services.apiService.routes.league_route import LeagueResponse
from services.repositories import ItemRepository
from pydantic import BaseModel
import pandas as pd
from services.repositories.item_repository.GetSnapshotForLeague import LeagueSnapshot

router = APIRouter(prefix="/dbDumps")



class LeagueSnapshotModel(BaseModel):
    leagueId: int
    priceLogs: list[LeagueSnapshot]

@router.get("/GetSnapshot/{leagueId:int}")
async def GetSnapshot(leagueId: int, repo: ItemRepository = Depends(get_item_repository)) -> StreamingResponse :
    result = await repo.GetSnapshotForLeague(leagueId)
    newList = [r.model_dump() for r in result]
    
    df = pd.DataFrame(newList)
    csv_string = df.to_csv(index=False)

    csv_buffer = io.BytesIO(csv_string.encode('utf-8'))

    return StreamingResponse(
        csv_buffer,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=data.csv"}
    )