from ..base_repository import BaseRepository, RepositoryModel, scalar_as


class CreateItemModel(RepositoryModel):
    base_item_id: int
    item_type: str


async def create_item(item: CreateItemModel) -> int:
    async with BaseRepository.get_db_cursor(row_factory=scalar_as(int)) as cursor:
        query = """
            INSERT INTO "Item" ("baseItemId", "itemType")
            VALUES (%s, %s)
            RETURNING "id"
        """

        await cursor.execute(query, (item.base_item_id, item.item_type))

        return await anext(cursor)


class CreateItem(BaseRepository):
    async def execute(self, item: CreateItemModel) -> int:
        return await create_item(item)
