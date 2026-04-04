import json
from typing import Optional

from ..base_repository import BaseRepository, RepositoryModel, scalar_as


class CreateBaseItemModel(RepositoryModel):
    type_id: int
    icon_url: Optional[str] = None
    item_metadata: Optional[dict] = None


async def create_base_item(base_item: CreateBaseItemModel) -> int:
    async with BaseRepository.get_db_cursor(row_factory=scalar_as(int)) as cursor:
        metadata_json = (
            json.dumps(base_item.item_metadata) if base_item.item_metadata is not None else None
        )

        query = """
            INSERT INTO "BaseItem" ("typeId", "iconUrl", "itemMetadata")
            VALUES (%s, %s, %s)
            RETURNING "id"
        """

        await cursor.execute(query, (base_item.type_id, base_item.icon_url, metadata_json))

        return await anext(cursor)


class CreateBaseItem(BaseRepository):
    async def execute(self, base_item: CreateBaseItemModel) -> int:
        return await create_base_item(base_item)
