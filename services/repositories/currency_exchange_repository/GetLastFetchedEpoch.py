from typing import Tuple, Optional
import json
from ..base_repository import BaseRepository
from pydantic import BaseModel
from psycopg.rows import class_row


class GetLastFetchedEpochModel(BaseModel):
    Epoch: int | None

class GetLastFetchedEpoch(BaseRepository):
    async def execute(self) -> GetLastFetchedEpochModel:
        async with self.get_db_cursor(rowFactory=class_row(GetLastFetchedEpochModel)) as cursor:
            query = """
                SELECT MAX("Epoch") AS "Epoch"
                FROM "CurrencyExchangeSnapshot"
            """
            await cursor.execute(query)
            
            return await cursor.fetchone() # type: ignore
