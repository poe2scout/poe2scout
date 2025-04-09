from typing import Tuple, Optional
from ..base_repository import BaseRepository
from pydantic import BaseModel
import json
from psycopg.types.json import Json




class UpdateUniqueIconUrl(BaseRepository):
    async def execute(self, iconUrl: str, id: int) -> int:

        uniqueItem_query = """
            UPDATE "UniqueItem"
            SET "iconUrl" = %(iconUrl)s
            WHERE "id" = %(id)s
        """

        rows = await self.execute_update(
            uniqueItem_query, params={
                "iconUrl":iconUrl, 
                "id":id
            })

        return rows
