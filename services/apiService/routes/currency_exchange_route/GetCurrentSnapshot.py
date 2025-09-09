from services.repositories.currency_exchange_repository.GetCurrentSnapshot import GetCurrencyExchangeModel
from . import router
from fastapi import HTTPException
from services.apiService.dependancies import CXRepoDep, ItemRepoDep


@router.get("")
async def Get(league: str, item_repo:  ItemRepoDep, cx_repo: CXRepoDep) -> GetCurrencyExchangeModel:
    leagueInDb = await item_repo.GetLeagueByValue(league)

    if not leagueInDb:
        raise HTTPException(400, "Invalid league name")

    getCurrencyExchangeResponse = await cx_repo.GetCurrencyExchange(leagueInDb.id)

    if not getCurrencyExchangeResponse:
        raise HTTPException(404, "No data for given league.")
    
    return getCurrencyExchangeResponse
