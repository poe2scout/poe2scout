import json

from ..base_repository import BaseRepository


async def set_unique_item_metadata(item_metadata: dict, id: int):
    async with BaseRepository.get_db_cursor() as cursor:
        query = """
            UPDATE "UniqueItem"
            SET "itemMetadata" = %(item_metadata)s
            WHERE "id" = %(id)s
        """

        await cursor.execute(
            query,
            params={"item_metadata": json.dumps(item_metadata), "id": id},
        )