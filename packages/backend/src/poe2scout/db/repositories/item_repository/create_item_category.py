from ..base_repository import BaseRepository, RepositoryModel, scalar_as


class CreateItemCategoryModel(RepositoryModel):
    id: str
    label: str


async def create_item_category(item_category: CreateItemCategoryModel) -> int:
    async with BaseRepository.get_db_cursor(row_factory=scalar_as(int)) as cursor:
        query = """
            INSERT INTO "ItemCategory" ("apiId", "label")
            VALUES (%s, %s)
            RETURNING "id"
        """

        await cursor.execute(query, (item_category.id, item_category.label))

        return await anext(cursor)


class CreateItemCategory(BaseRepository):
    async def execute(self, item_category: CreateItemCategoryModel) -> int:
        return await create_item_category(item_category)
