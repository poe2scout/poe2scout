from psycopg.rows import class_row

from ..base_repository import BaseRepository, RepositoryModel


class League(RepositoryModel):
    league_id: int
    value: str
    base_currency_item_id: int
    base_currency_api_id: str
    base_currency_text: str
    current_league: bool


async def get_current_leagues(game_id: int) -> list[League]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(League)) as cursor:
        query = """
            SELECT l.league_id,
                   l.value,
                   l.base_currency_item_id,
                   ci.api_id AS base_currency_api_id,
                   ci.text AS base_currency_text,
                   l.current_league
              FROM league AS l
              JOIN currency_item AS ci
                ON ci.item_id = l.base_currency_item_id
            WHERE current_league = true
              AND game_id = %(game_id)s
        """

        params = {
            "game_id": game_id
        }

        await cursor.execute(query, params)

        return await cursor.fetchall()


async def get_leagues(game_id: int) -> list[League]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(League)) as cursor:
        query = """
            SELECT l.league_id,
                   l.value,
                   l.base_currency_item_id,
                   ci.api_id AS base_currency_api_id,
                   ci.text AS base_currency_text,
                   l.current_league
              FROM league AS l
              JOIN currency_item AS ci
                ON ci.item_id = l.base_currency_item_id
             WHERE l.game_id = %(game_id)s
        """

        params = {
            "game_id": game_id
        }
        await cursor.execute(query, params)

        return await cursor.fetchall()

async def get_league(league_id: int) -> League:
    async with BaseRepository.get_db_cursor(row_factory=class_row(League)) as cursor:
        query = """
            SELECT l.league_id,
                   l.value,
                   l.base_currency_item_id,
                   ci.api_id AS base_currency_api_id,
                   ci.text AS base_currency_text,
                   l.current_league
              FROM league AS l
              JOIN currency_item AS ci
                ON ci.item_id = l.base_currency_item_id
             WHERE l.league_id = %(league_id)s
        """

        params = {
            "league_id": league_id
        }
        await cursor.execute(query, params)

        return await anext(cursor)
