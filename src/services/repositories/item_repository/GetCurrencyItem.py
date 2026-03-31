
from services.repositories.models import CurrencyItem
from ..base_repository import BaseRepository
from pydantic import BaseModel


class GetCurrencyItemIdModel(BaseModel):
    apiId: str


class GetCurrencyItem(BaseRepository):
    async def execute(self, apiId: str) -> CurrencyItem:
        item_query = """
            SELECT ci."id", 
                   ci."itemId", 
                   ci."apiId", 
                   ci."text", 
                   ci."iconUrl", 
                   ci."currencyCategoryId", 
                   cc."label", 
                   cc."apiId" as "categoryApiId" 
              FROM "CurrencyItem" as ci
              JOIN "CurrencyCategory" as cc on ci."currencyCategoryId" = cc."id"
             WHERE ci."apiId" = %s
        """

        currencyItem = (await self.execute_query(item_query, (apiId,)))[0]

        return CurrencyItem(**currencyItem)
