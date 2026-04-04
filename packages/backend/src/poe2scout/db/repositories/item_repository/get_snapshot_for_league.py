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
            , pl.created_at AS "created_at"
            , pl."quantity"
            , ci.api_id AS "currency_item_text"
            , ui."text" AS "unique_item_text"
        FROM price_log AS pl
        JOIN item AS i ON pl.item_id = i.item_id
        LEFT JOIN currency_item AS ci ON i.item_id = ci.item_id
        LEFT JOIN unique_item AS ui ON i.item_id = ui.item_id
        WHERE league_id = %(league_id)s
        ORDER BY created_at DESC
        """

        await cursor.execute(query, {"league_id": league_id})

        return await cursor.fetchall()
