import itertools
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from psycopg.rows import class_row

from ..base_repository import BaseRepository, RepositoryModel

class Realm(RepositoryModel):
    realm_id: int
    game_id: int

async def get_realm(api_id: str) -> Realm:
    async with BaseRepository.get_db_cursor(row_factory=class_row(Realm)) as cursor:
        query = """
SELECT realm_id
     , game_id
  FROM realm
 WHERE api_id = %(api_id)s;
        """
        params = {"api_id": api_id}

        await cursor.execute(query, params)
        return await anext(cursor)


