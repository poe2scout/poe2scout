from ..base_repository import BaseRepository
import json


class SetUniqueItemMetadata(BaseRepository):
    async def execute(self, itemMetadata: dict, id: int):
        async with self.get_db_cursor() as cursor:

            query = """
                UPDATE "UniqueItem"
                SET "itemMetadata" = %(itemMetadata)s
                WHERE "id" = %(id)s
            """

            await cursor.execute(
                query,
                params={"itemMetadata": json.dumps(itemMetadata), "id": id},
            )
