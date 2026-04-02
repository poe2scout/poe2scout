from fastapi import APIRouter


router = APIRouter(prefix="/CurrencyExchange", tags=["CurrencyExchange"])

from .GetSnapshot import GetSnapshot
from .GetSnapshotHistory import GetSnapshotHistory
from .GetSnapshotPairs import GetSnapshotPairs
from .GetPairHistory import GetPairHistory
