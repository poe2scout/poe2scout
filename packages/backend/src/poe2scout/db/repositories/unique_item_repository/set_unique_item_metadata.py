import json

from ..base_repository import BaseRepository


async def set_unique_item_metadata(item_metadata: dict, unique_item_id: int):
    async with BaseRepository.get_db_cursor() as cursor:
        query = """
            UPDATE unique_item
            SET item_metadata = %(item_metadata)s
            WHERE unique_item_id = %(unique_item_id)s
        """

        await cursor.execute(
            query,
            params={
                "item_metadata": json.dumps(item_metadata),
                "unique_item_id": unique_item_id,
            },
        )
