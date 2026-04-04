from ..base_repository import BaseRepository, scalar_as


async def get_prices_checked(epoch: int, league_id: int) -> bool:
    async with BaseRepository.get_db_cursor(row_factory=scalar_as(int)) as cursor:
        query = """
            SELECT
                CASE
                    WHEN EXISTS(
                        SELECT 1 FROM price_log
                        WHERE created_at = to_timestamp(%s)
                        AND league_id = %s
                    )
                    THEN 1
                    ELSE 0
                END;
        """

        return bool(await anext((await cursor.execute(query, (epoch, league_id)))))