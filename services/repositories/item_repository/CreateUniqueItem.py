from typing import Optional
from ..base_repository import BaseRepository
from pydantic import BaseModel


class CreateUniqueItemModel(BaseModel):
    itemId: int
    iconUrl: Optional[str] = None
    text: str
    name: str


class CreateUniqueItem(BaseRepository):
    async def execute(self, uniqueItem: CreateUniqueItemModel) -> int:
        uniqueItem_query = """
            INSERT INTO "UniqueItem" ("itemId", "iconUrl", "text", "name")
            VALUES (%(itemId)s, %(iconUrl)s, %(text)s, %(name)s)
            RETURNING "id"
        """

        uniqueItemId = await self.execute_single(
            uniqueItem_query,
            params={
                "itemId": uniqueItem.itemId,
                "iconUrl": uniqueItem.iconUrl,
                "text": uniqueItem.text,
                "name": uniqueItem.name,
            },
        )

        return uniqueItemId
