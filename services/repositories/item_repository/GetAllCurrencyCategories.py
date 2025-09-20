from typing import List
from ..base_repository import BaseRepository
from pydantic import BaseModel


class CurrencyCategory(BaseModel):
    id: int
    apiId: str
    label: str


class GetAllCurrencyCategories(BaseRepository):
    async def execute(self) -> List[CurrencyCategory]:
        currencyCategory_query = """
            SELECT "id", "apiId", "label" FROM "CurrencyCategory"
        """

        currencyCategories = await self.execute_query(currencyCategory_query)

        return [
            CurrencyCategory(**currencyCategory)
            for currencyCategory in currencyCategories
        ]
