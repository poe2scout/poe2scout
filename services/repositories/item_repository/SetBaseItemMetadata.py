from typing import Tuple, Optional
from ..base_repository import BaseRepository
from pydantic import BaseModel
import json
from psycopg.types.json import Json




class SetBaseItemMetadata(BaseRepository):
    async def execute(self, itemMetadata: dict, id: int) -> int:

        baseItem_query = """
            UPDATE "BaseItem"
            SET "itemMetadata" = %(itemMetadata)s
            WHERE "id" = %(id)s
        """

        rows = await self.execute_update(
            baseItem_query, params={
                "itemMetadata":json.dumps(itemMetadata), 
                "id":id
            })
        

        return rows
