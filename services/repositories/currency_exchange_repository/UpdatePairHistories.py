from typing import Tuple, Optional
import json
from ..base_repository import BaseRepository
from pydantic import BaseModel
from psycopg.rows import class_row


class UpdatePairHistories(BaseRepository):
    async def execute(self):
        async with self.get_db_cursor() as cursor:
            query = """
SELECT update_currency_history_incrementally();
            """

            await cursor.execute(query)

            return 
        
            