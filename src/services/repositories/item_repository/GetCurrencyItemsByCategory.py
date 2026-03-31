from typing import List

from services.repositories.models import CurrencyItem
from ..base_repository import BaseRepository


class GetCurrencyItemsByCategory(BaseRepository):
    async def execute(self, category: str) -> List[CurrencyItem]:
        currencyItem_query = """
            SELECT ci."id", ci."itemId", cc."label", cc."apiId" as "categoryApiId", ci."apiId", ci."text", ci."iconUrl", ci."currencyCategoryId", ci."itemMetadata" FROM "CurrencyItem" AS ci
            JOIN "CurrencyCategory" AS cc ON ci."currencyCategoryId" = cc."id"
            WHERE cc."apiId" ILIKE %s
        """
        params = (category,)

        currencyItems = await self.execute_query(currencyItem_query, params)

        return [CurrencyItem(**currencyItem) for currencyItem in currencyItems]
