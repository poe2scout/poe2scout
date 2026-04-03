from ..base_repository import BaseRepository
import json


class SetCurrencyItemMetadata(BaseRepository):
    async def execute(self, itemMetadata: dict, id: int):
        async with self.get_db_cursor() as cursor:
            query = """
                UPDATE "CurrencyItem"
                SET "itemMetadata" = %(itemMetadata)s
                WHERE "id" = %(id)s
            """

            await cursor.execute(
                query,
                params={"itemMetadata": json.dumps(itemMetadata), "id": id},
            )
