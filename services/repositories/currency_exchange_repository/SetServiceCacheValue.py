from ..base_repository import BaseRepository


class SetServiceCacheValue(BaseRepository):
    async def execute(self, serviceName: str, value: int):
        async with self.get_db_cursor() as cursor:
            query = """
                UPDATE "ServiceCache"
                   SET "Value" = %(value)s
                 WHERE "ServiceName" = %(serviceName)s
            """

            params = {"serviceName": serviceName, "value": value}

            await cursor.execute(query, params)

            return
