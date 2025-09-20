from ..base_repository import BaseRepository


class UpdateUniqueIconUrl(BaseRepository):
    async def execute(self, iconUrl: str, id: int) -> int:
        uniqueItem_query = """
            UPDATE "UniqueItem"
            SET "iconUrl" = %(iconUrl)s
            WHERE "id" = %(id)s
        """

        rows = await self.execute_update(
            uniqueItem_query, params={"iconUrl": iconUrl, "id": id}
        )

        return rows
