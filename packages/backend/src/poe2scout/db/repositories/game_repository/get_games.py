from ..base_repository import BaseRepository, RepositoryModel
from psycopg.rows import class_row

class Game(RepositoryModel):
    game_id: int
    api_id: str
    label: str
    ggg_api_trade_identifier: str
    default_league_id: int

async def get_games() -> list[Game]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(Game)) as cursor:
        query = """
SELECT game_id
     , api_id
     , label
     , ggg_api_trade_identifier
     , default_league_id
  FROM game;
"""
        await cursor.execute(query)
        return await cursor.fetchall()

