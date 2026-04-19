from poe2scout.db.repositories.base_repository import BaseRepository, scalar_as


async def get_existing_snapshot_league_ids(epoch: int, realm_id: int) -> list[int]:
    async with BaseRepository.get_db_cursor(row_factory=scalar_as(int)) as cursor:
        query = """
            SELECT league_id
              FROM currency_exchange_snapshot
             WHERE epoch = %(epoch)s
               AND realm_id = %(realm_id)s
        """

        params = {
            "epoch": epoch,
            "realm_id": realm_id,
        }

        await cursor.execute(query, params)

        return await cursor.fetchall()
