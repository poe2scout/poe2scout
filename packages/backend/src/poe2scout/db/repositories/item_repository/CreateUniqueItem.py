from typing import Optional
from ..base_repository import BaseRepository, scalar_as
from pydantic import BaseModel


class CreateUniqueItemModel(BaseModel):
    itemId: int
    iconUrl: Optional[str] = None
    text: str
    name: str


class CreateUniqueItem(BaseRepository):
    async def execute(self, uniqueItem: CreateUniqueItemModel) -> int:
        async with self.get_db_cursor(rowFactory=scalar_as(int)) as cursor:

            query = """
                INSERT INTO "UniqueItem" ("itemId", "iconUrl", "text", "name")
                VALUES (%(itemId)s, %(iconUrl)s, %(text)s, %(name)s)
                RETURNING "id"
            """

            await cursor.execute(
                query,
                params={
                    "itemId": uniqueItem.itemId,
                    "iconUrl": uniqueItem.iconUrl,
                    "text": uniqueItem.text,
                    "name": uniqueItem.name,
                },
            )

            return await anext(cursor)
