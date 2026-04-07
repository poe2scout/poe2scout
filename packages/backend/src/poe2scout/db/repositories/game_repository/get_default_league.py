from ..base_repository import BaseRepository, scalar_as

async def get_default_league(game_id: int) -> int:
    async with BaseRepository.get_db_cursor(row_factory=scalar_as(int)) as cursor:
        query = """
SELECT default_league_id
  FROM game
 WHERE game_id = %(game_id)s;
        """
        params = {"game_id": game_id}

        await cursor.execute(query, params)
        return await anext(cursor)

