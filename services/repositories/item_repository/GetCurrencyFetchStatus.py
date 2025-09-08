from datetime import datetime
from decimal import Decimal
from typing import List
from ..base_repository import BaseRepository
from pydantic import BaseModel
from psycopg.rows import class_row

class GetCurrencyFetchStatus(BaseRepository):
    async def execute(self, startTime: datetime) -> bool:
        async with self.get_db_cursor() as cursor:
            query = """
                SELECT 1
                  FROM "CurrencyItem" AS ci
                  JOIN "PriceLog" AS pl ON ci."itemId" = pl."itemId"
                 WHERE pl."createdAt" >= %(startTime)s
            """

            params = {
            "startTime": startTime,
            }

            await cursor.execute(query, params)

            if cursor.rowcount == 0:
                return False
            else: 
                return True