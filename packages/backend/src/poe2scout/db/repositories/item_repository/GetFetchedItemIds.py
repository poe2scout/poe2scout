from ..base_repository import BaseRepository, scalar_as
from datetime import datetime, timedelta


class GetFetchedItemIds(BaseRepository):
    async def execute(self, currentHour: str, leagueId: int) -> list[int]:
        async with self.get_db_cursor(
            rowFactory=scalar_as(int)
        ) as cursor:

            currentHourInt = int(currentHour)
            ranges = [[0, 12], [12, 24]]

            currentStart = None
            currentEnd = None
            for range in ranges:
                if currentHourInt >= range[0] and currentHourInt < range[1]:
                    currentStart = range[0]
                    currentEnd = range[1]
            
            assert currentStart is not None and currentEnd is not None

            currentStart = datetime.now().replace(
                hour=currentStart, minute=0, second=0, microsecond=0
            )
            currentDay = datetime.now().day
            if currentEnd == 24:
                currentEnd = 0
                currentDay = (datetime.now() + timedelta(days=1)).day
            currentEnd = datetime.now().replace(
                day=currentDay, hour=currentEnd, minute=0, second=0, microsecond=0
            )

            query = """
                SELECT DISTINCT i."id" FROM "Item" as i
                JOIN "PriceLog" as pl ON i."id" = pl."itemId"
                JOIN "League" as l ON pl."leagueId" = l."id"
                WHERE pl."createdAt" > %s AND pl."createdAt" < %s AND l."id" = %s
            """
            await cursor.execute(
                query, (currentStart, currentEnd, leagueId)
            )

            return await cursor.fetchall()
