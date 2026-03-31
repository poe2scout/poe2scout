from typing import Awaitable
from ..base_repository import BaseRepository


class OverwriteCategory(BaseRepository):
    async def execute(self, categoryId: int, newCategoryId: int) -> Awaitable[int]:
        item_query = """
            UPDATE "ItemType" as it
            SET "categoryId" = %(newCategoryId)s
            Where "categoryId" = %(categoryId)s
        """

        await self.execute_update(
            item_query, {"categoryId": categoryId, "newCategoryId": newCategoryId}
        )
        return
