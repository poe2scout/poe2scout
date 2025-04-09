from typing import Optional
from ..base_repository import BaseRepository
from pydantic import BaseModel


class CreateCurrencyItemModel(BaseModel):
    itemId: int
    currencyCategoryId: int
    apiId: str
    text: str
    image: Optional[str] = None


class CreateCurrencyItem(BaseRepository):
    async def execute(self, currencyItem: CreateCurrencyItemModel) -> int: 
        
        currencyItem_query = """
            INSERT INTO "CurrencyItem" ("itemId", "currencyCategoryId", "apiId", "text", "iconUrl")
            VALUES (%s, %s, %s, %s, %s)
            RETURNING "id"
        """

        currencyItemId = await self.execute_single(
            currencyItem_query, (currencyItem.itemId, currencyItem.currencyCategoryId, currencyItem.apiId, currencyItem.text, currencyItem.image))

        return currencyItemId
