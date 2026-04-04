from ..base_repository import BaseRepository, RepositoryModel, scalar_as


class CreateItemTypeModel(RepositoryModel):
    value: str
    category_id: int


async def create_item_type(item_type: CreateItemTypeModel) -> int:
    async with BaseRepository.get_db_cursor(row_factory=scalar_as(int)) as cursor:
        query = """
            INSERT INTO "ItemType" ("value", "categoryId")
            VALUES (%s, %s)
            RETURNING "id"
        """

        await cursor.execute(query, (item_type.value, item_type.category_id))

        return await anext(cursor)


class CreateItemType(BaseRepository):
    async def execute(self, item_type: CreateItemTypeModel) -> int:
        return await create_item_type(item_type)
