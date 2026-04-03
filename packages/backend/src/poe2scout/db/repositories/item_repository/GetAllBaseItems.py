from typing import Optional, List

from psycopg.rows import class_row
from ..base_repository import BaseRepository
from pydantic import BaseModel


class BaseItem(BaseModel):
    id: int
    typeId: int
    iconUrl: Optional[str] = None
    itemMetadata: Optional[dict] = None


class GetAllBaseItems(BaseRepository):
    async def execute(self) -> List[BaseItem]:
        async with self.get_db_cursor(
            rowFactory=class_row(BaseItem)
        ) as cursor:
            query = """
                SELECT "bi"."id"
                    , "bi"."typeId"
                    , "bi"."iconUrl"
                    , "bi"."itemMetadata" 
                FROM "BaseItem" as bi
            """

            await cursor.execute(query)

            return await cursor.fetchall()
