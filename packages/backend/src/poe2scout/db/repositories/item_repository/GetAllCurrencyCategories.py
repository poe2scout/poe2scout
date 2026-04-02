from poe2scout.db.repositories.item_repository.GetAllItemCategories import ItemCategory

from ..base_repository import BaseRepository

class GetAllCurrencyCategories(BaseRepository):
    async def execute(self) -> list[ItemCategory]:
        currencyCategory_query = """
            SELECT "id", "apiId", "label" FROM "CurrencyCategory"
        """

        currencyCategories = await self.execute_query(currencyCategory_query)

        return [
            ItemCategory(**currencyCategory)
            for currencyCategory in currencyCategories
        ]
