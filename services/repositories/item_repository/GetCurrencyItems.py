from typing import Optional, Awaitable
from ..base_repository import BaseRepository
from pydantic import BaseModel
from .GetAllCurrencyItems import CurrencyItem



class GetCurrencyItems(BaseRepository):
    async def execute(self, apiIds: list[str]) -> list[CurrencyItem]:
        item_query = """
SELECT ci."id"
     , ci."itemId"
     , ci."apiId"
     , ci."text"
     , ci."iconUrl"
     , ci."currencyCategoryId"
     , cc."label"
     , cc."apiId" AS "categoryApiId" 
  FROM "CurrencyItem" AS ci
  JOIN "CurrencyCategory" AS cc ON ci."currencyCategoryId" = cc."id"
 WHERE ci."apiId" = ANY(%s)
        """

        currencyItems = (await self.execute_query(
            item_query, (apiIds,)))

        return [CurrencyItem(**currencyItem) for currencyItem in currencyItems]
