from ..base_repository import BaseRepository


class IsItemACurrency(BaseRepository):
    async def execute(self, itemId: int) -> bool:
        item_query = """
            SELECT ci."id", ci."itemId", ci."apiId", ci."text", ci."iconUrl", ci."currencyCategoryId", cc."label", cc."apiId" as "categoryApiId" FROM "CurrencyItem" as ci
            JOIN "CurrencyCategory" as cc on ci."currencyCategoryId" = cc."id"
            WHERE ci."itemId" = %s
        """

        currencyItem = await self.execute_query(item_query, (itemId,))

        return len(currencyItem) == 1
