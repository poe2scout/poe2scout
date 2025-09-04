from typing import Tuple, Optional
import json
from ..base_repository import BaseRepository
from pydantic import BaseModel
from psycopg.rows import class_row


class GetServiceCacheValueModel(BaseModel):
    Value: int | None

class GetServiceCacheValue(BaseRepository):
    async def execute(self, serviceName: str) -> GetServiceCacheValueModel:
        async with self.get_db_cursor(rowFactory=class_row(GetServiceCacheValueModel)) as cursor:
            query = """
                SELECT "Value"
                  FROM "ServiceCache"
                 WHERE "ServiceName" = %(serviceName)s
            """

            params = {
                "serviceName": serviceName
            }

            await cursor.execute(query, params)
            
            return await cursor.fetchone()  # type: ignore
