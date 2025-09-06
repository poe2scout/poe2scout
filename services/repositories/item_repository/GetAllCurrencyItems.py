from typing import Tuple, Optional, List
from ..base_repository import BaseRepository
from pydantic import BaseModel

class CurrencyItem(BaseModel):
    id: int
    itemId: int
    currencyCategoryId: int
    apiId: str
    text: str
    categoryApiId: str
    iconUrl: Optional[str] = None
    itemMetadata: Optional[dict] = None

    
class GetAllCurrencyItems(BaseRepository):
    async def execute(self) -> List[CurrencyItem]:
        currencyItem_query = """
            SELECT ci."id", ci."itemId", ci."currencyCategoryId", cc."apiId" as "categoryApiId", ci."apiId", ci."text", ci."iconUrl", "itemMetadata" FROM "CurrencyItem" as ci
			JOIN "CurrencyCategory" as cc on ci."currencyCategoryId" = cc.id
        """

        currencyItems = await self.execute_query(
            currencyItem_query)

        return [CurrencyItem(**currencyItem) for currencyItem in currencyItems]
