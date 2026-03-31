from typing import List

from services.repositories.models import CurrencyItem
from ..base_repository import BaseRepository


class GetAllCurrencyItems(BaseRepository):
    async def execute(self) -> List[CurrencyItem]:
        currencyItem_query = """
            SELECT ci."id", ci."itemId", ci."currencyCategoryId", cc."apiId" as "categoryApiId", ci."apiId", ci."text", ci."iconUrl", "itemMetadata" FROM "CurrencyItem" as ci
			JOIN "CurrencyCategory" as cc on ci."currencyCategoryId" = cc.id
        """

        currencyItems = await self.execute_query(currencyItem_query)

        return [CurrencyItem(**currencyItem) for currencyItem in currencyItems]
