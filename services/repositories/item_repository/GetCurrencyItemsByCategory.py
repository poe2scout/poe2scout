from typing import Tuple, Optional, List
from ..base_repository import BaseRepository
from .GetAllCurrencyItems import CurrencyItem


class GetCurrencyItemsByCategory(BaseRepository):
    async def execute(self, category: str, search: str = "") -> List[CurrencyItem]:
        currencyItem_query = """
            SELECT ci."id", ci."itemId", cc."label", cc."apiId" as "categoryApiId", ci."apiId", ci."text", ci."iconUrl", ci."currencyCategoryId", ci."itemMetadata" FROM "CurrencyItem" AS ci
            JOIN "CurrencyCategory" AS cc ON ci."currencyCategoryId" = cc."id"
            WHERE cc."apiId" ILIKE %s
        """
        params = (category,)
        if search:
            currencyItem_query += """ AND ci."text" ILIKE %s"""
            params += (search,)

        currencyItems = await self.execute_query(
            currencyItem_query, params)

        return [CurrencyItem(**currencyItem) for currencyItem in currencyItems]
