from typing import Tuple, Optional
import json
from ..base_repository import BaseRepository
from pydantic import BaseModel
from psycopg.rows import class_row


class SetServiceCacheValue(BaseRepository):
    async def execute(self, serviceName: str, value: int):
        async with self.get_db_cursor() as cursor:
            query = """
                UPDATE "ServiceCache"
                   SET "Value" = %(value)s
                 WHERE "ServiceName" = %(serviceName)s
            """

            params = {
                "serviceName": serviceName,
                "value": value
            }

            await cursor.execute(query, params)
            
            return 
        
            