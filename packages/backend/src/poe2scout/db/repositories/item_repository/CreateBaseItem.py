from typing import Optional
import json
from ..base_repository import BaseRepository, scalar_as
from pydantic import BaseModel


class CreateBaseItemModel(BaseModel):
    typeId: int
    iconUrl: Optional[str] = None
    itemMetadata: Optional[dict] = None


class CreateBaseItem(BaseRepository):
    async def execute(self, baseItem: CreateBaseItemModel) -> int:
        async with self.get_db_cursor(rowFactory=scalar_as(int)) as cursor:
            # Convert itemMetadata dict to JSON string if it exists
            metadata_json = (
                json.dumps(baseItem.itemMetadata)
                if baseItem.itemMetadata is not None
                else None
            )

            query = """
                INSERT INTO "BaseItem" ("typeId", "iconUrl", "itemMetadata")
                VALUES (%s, %s, %s)
                RETURNING "id"
            """

            await cursor.execute(
                query, (baseItem.typeId, baseItem.iconUrl, metadata_json)
            )

            return await anext(cursor)
