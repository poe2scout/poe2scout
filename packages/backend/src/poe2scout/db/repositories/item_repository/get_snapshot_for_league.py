from datetime import datetime

from psycopg.rows import class_row

from ..base_repository import BaseRepository, RepositoryModel


class LeagueSnapshot(RepositoryModel):
    price: float
    created_at: datetime
    quantity: int
    currency_item_text: str
    unique_item_text: str


async def get_snapshot_for_league(league_id: int) -> list[LeagueSnapshot]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(LeagueSnapshot)) as cursor:
        query = """
        SELECT pl."price"
            , pl."createdAt" AS "created_at"
            , pl."quantity"
            , ci."apiId" AS "currency_item_text"
            , ui."text" AS "unique_item_text"
        FROM "PriceLog" AS pl
        JOIN "Item" AS i ON pl."itemId" = i."id"
        LEFT JOIN "CurrencyItem" AS ci ON i."id" = ci."itemId"
        LEFT JOIN "UniqueItem" AS ui ON i."id" = ui."itemId"
        WHERE "leagueId" = %(league_id)s
        ORDER BY "createdAt" DESC
        """

        await cursor.execute(query, {"league_id": league_id})

        return await cursor.fetchall()
