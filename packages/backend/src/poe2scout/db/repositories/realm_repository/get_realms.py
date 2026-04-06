from psycopg.rows import class_row

from ..base_repository import BaseRepository, RepositoryModel

class Realm(RepositoryModel):
    realm_id: int
    game_id: int
    api_id: str

async def get_realms() -> list[Realm]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(Realm)) as cursor:
        query = """
SELECT realm_id
     , game_id
     , api_id
  FROM realm;
        """

        await cursor.execute(query)
        return await cursor.fetchall()


