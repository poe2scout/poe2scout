from ..base_repository import BaseRepository
from pydantic import BaseModel


class CreateItemCategoryModel(BaseModel):
    id: str
    label: str


class CreateItemCategory(BaseRepository):
    async def execute(self, itemCategory: CreateItemCategoryModel) -> int:
        itemCategory_query = """
            INSERT INTO "ItemCategory" ("apiId", "label")
            VALUES (%s, %s)
            RETURNING "id"
        """

        itemCategoryId = await self.execute_single(
            itemCategory_query, (itemCategory.id, itemCategory.label)
        )

        return itemCategoryId
