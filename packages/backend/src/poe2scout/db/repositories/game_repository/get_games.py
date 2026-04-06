from ..base_repository import BaseRepository, RepositoryModel, scalar_as
from psycopg.rows import class_row

class Game(RepositoryModel):
    game_id: int
    api_id: str
    label: str
    ggg_api_trade_identifier: str

async def get_games() -> list[Game]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(Game)) as cursor:
        query = """
SELECT game_id
     , api_id
     , label
     , ggg_api_trade_identifier
  FROM game;
"""
        await cursor.execute(query)
        return await cursor.fetchall()


