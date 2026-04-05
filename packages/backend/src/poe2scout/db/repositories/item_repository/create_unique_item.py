from typing import Optional

from ..base_repository import BaseRepository, RepositoryModel, scalar_as


class CreateUniqueItemModel(RepositoryModel):
    item_id: int
    icon_url: Optional[str] = None
    text: str
    name: str


async def create_unique_item(unique_item: CreateUniqueItemModel) -> int:
    async with BaseRepository.get_db_cursor(row_factory=scalar_as(int)) as cursor:
        query = """
            INSERT INTO unique_item (item_id, icon_url, text, name)
            VALUES (%(item_id)s, %(icon_url)s, %(text)s, %(name)s)
            RETURNING unique_item_id
        """

        await cursor.execute(
            query,
            params={
                "item_id": unique_item.item_id,
                "icon_url": unique_item.icon_url,
                "text": unique_item.text,
                "name": unique_item.name,
            },
        )

        return await anext(cursor)


class CreateUniqueItem(BaseRepository):
    async def execute(self, unique_item: CreateUniqueItemModel) -> int:
        return await create_unique_item(unique_item)
