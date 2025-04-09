from typing import Tuple, Optional
import json
from ..base_repository import BaseRepository
from pydantic import BaseModel

class CreateBaseItemModel(BaseModel):
    typeId: int
    iconUrl: Optional[str] = None
    itemMetadata: Optional[dict] = None


class CreateBaseItem(BaseRepository):
    async def execute(self, baseItem: CreateBaseItemModel) -> int:
        # Convert itemMetadata dict to JSON string if it exists
        metadata_json = json.dumps(baseItem.itemMetadata) if baseItem.itemMetadata is not None else None

        baseItem_query = """
            INSERT INTO "BaseItem" ("typeId", "iconUrl", "itemMetadata")
            VALUES (%s, %s, %s)
            RETURNING "id"
        """

        baseItemId = await self.execute_single(
            baseItem_query, (baseItem.typeId, baseItem.iconUrl, metadata_json))

        return baseItemId
