import json

from ..base_repository import BaseRepository


async def set_base_item_metadata(item_metadata: dict, base_item_id: int):
    async with BaseRepository.get_db_cursor() as cursor:
        query = """
            UPDATE base_item
            SET item_metadata = %(item_metadata)s
            WHERE base_item_id = %(base_item_id)s
        """

        await cursor.execute(
            query,
            params={"item_metadata": json.dumps(item_metadata), "base_item_id": base_item_id},
        )
