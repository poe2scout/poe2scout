from ..base_repository import BaseRepository, scalar_as


class GetPricesChecked(BaseRepository):
    async def execute(self, epoch: int, leagueId: int) -> bool:
        async with self.get_db_cursor(
            rowFactory=scalar_as(int)
        ) as cursor:
            query = """
                SELECT
                    CASE
                        WHEN EXISTS(
                            SELECT 1 FROM "PriceLog"
                            WHERE "createdAt" = to_timestamp(%s)
                            AND "leagueId" = %s
                        )
                        THEN 1
                        ELSE 0
                    END;
            """

            return bool(
                await anext((await cursor.execute(query, (epoch, leagueId))))
            )
