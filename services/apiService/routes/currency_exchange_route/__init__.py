from fastapi import APIRouter


router = APIRouter(prefix="/currencyExchange", tags=["currencyExchange"])

from .Get import Get
from .GetHistory import GetHistory