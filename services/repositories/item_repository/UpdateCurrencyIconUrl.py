from ..base_repository import BaseRepository


class UpdateCurrencyIconUrl(BaseRepository):
    async def execute(self, iconUrl: str, id: int) -> int:
        currencyItem_query = """
            UPDATE "CurrencyItem"
            SET "iconUrl" = %(iconUrl)s
            WHERE "id" = %(id)s
        """

        rows = await self.execute_update(
            currencyItem_query, params={"iconUrl": iconUrl, "id": id}
        )

        return rows
