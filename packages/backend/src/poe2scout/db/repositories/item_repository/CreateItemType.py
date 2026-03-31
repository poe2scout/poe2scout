from ..base_repository import BaseRepository
from pydantic import BaseModel


class CreateItemTypeModel(BaseModel):
    value: str
    categoryId: int


class CreateItemType(BaseRepository):
    async def execute(self, itemType: CreateItemTypeModel) -> int:
        itemType_query = """
            INSERT INTO "ItemType" ("value", "categoryId")
            VALUES (%s, %s)
            RETURNING "id"
        """

        itemTypeId = await self.execute_single(
            itemType_query, (itemType.value, itemType.categoryId)
        )

        return itemTypeId
