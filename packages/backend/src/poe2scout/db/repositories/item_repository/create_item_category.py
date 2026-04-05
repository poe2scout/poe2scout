from ..base_repository import BaseRepository, RepositoryModel, scalar_as


class CreateItemCategoryModel(RepositoryModel):
    api_id: str
    label: str


async def create_item_category(item_category: CreateItemCategoryModel) -> int:
    async with BaseRepository.get_db_cursor(row_factory=scalar_as(int)) as cursor:
        query = """
            INSERT INTO item_category (api_id, label)
            VALUES (%s, %s)
            RETURNING item_category_id
        """

        await cursor.execute(query, (item_category.api_id, item_category.label))

        return await anext(cursor)


class CreateItemCategory(BaseRepository):
    async def execute(self, item_category: CreateItemCategoryModel) -> int:
        return await create_item_category(item_category)
