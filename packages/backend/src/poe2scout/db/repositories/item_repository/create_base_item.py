import json
from typing import Optional

from ..base_repository import BaseRepository, RepositoryModel, scalar_as


class CreateBaseItemModel(RepositoryModel):
    game_id: int
    item_type_id: int
    icon_url: Optional[str] = None
    item_metadata: Optional[dict] = None


async def create_base_item(base_item: CreateBaseItemModel) -> int:
    async with BaseRepository.get_db_cursor(row_factory=scalar_as(int)) as cursor:
        metadata_json = (
            json.dumps(base_item.item_metadata) if base_item.item_metadata is not None else None
        )

        query = """
            INSERT INTO base_item (item_type_id, icon_url, item_metadata, game_id)
            VALUES (%s, %s, %s, %s)
            RETURNING base_item_id
        """

        await cursor.execute(
            query, 
            (base_item.item_type_id, 
             base_item.icon_url, 
             metadata_json, 
             base_item.game_id)
        )

        return await anext(cursor)


class CreateBaseItem(BaseRepository):
    async def execute(self, base_item: CreateBaseItemModel) -> int:
        return await create_base_item(base_item)
