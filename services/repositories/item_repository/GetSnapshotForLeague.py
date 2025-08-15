from datetime import datetime
from typing import List, Awaitable, Optional
from ..base_repository import BaseRepository
from pydantic import BaseModel
from psycopg.rows import class_row

class LeagueSnapshot(BaseModel):
    price: float
    createdAt: datetime
    quantity: int
    currencyItemApiId: Optional[str]
    currencyItemText: Optional[str]
    uniqueItemText: Optional[str]

class GetSnapshotForLeague(BaseRepository):
    async def execute(self, leagueId: int) -> List[LeagueSnapshot]:
        async with self.get_db_cursor(rowFactory=class_row(LeagueSnapshot)) as cursor:
            await cursor.execute("""
            SELECT pl."price"
                , pl."createdAt"
                , pl."quantity"
                , ci."apiId" AS "currencyItemApiId"
                , ci."text" AS "currencyItemText"
                , ui."text" AS "uniqueItemText"
            FROM "PriceLog" AS pl
            JOIN "Item" AS i ON pl."itemId" = i."id"
            LEFT JOIN "CurrencyItem" AS ci ON i."id" = ci."itemId"
            LEFT JOIN "UniqueItem" AS ui ON i."id" = ui."itemId"
            WHERE "leagueId" = %(leagueId)s
            ORDER BY "createdAt" DESC
            """, {"leagueId": leagueId})


            return await cursor.fetchall()
