from typing import Tuple, Optional
from ..base_repository import BaseRepository
from pydantic import BaseModel

class CreateCurrencyCategoryModel(BaseModel):
    id: str
    label: str


class CreateCurrencyCategory(BaseRepository):
    async def execute(self, currencyCategory: CreateCurrencyCategoryModel) -> int:
        currencyCategory_query = """
            INSERT INTO "CurrencyCategory" ("apiId", "label")
            VALUES (%s, %s)
            RETURNING "id"
        """

        currencyCategoryId = await self.execute_single(
            currencyCategory_query, (currencyCategory.id, currencyCategory.label))

        return currencyCategoryId
