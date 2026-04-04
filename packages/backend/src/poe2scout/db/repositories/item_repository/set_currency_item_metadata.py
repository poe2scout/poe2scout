import json

from ..base_repository import BaseRepository


async def set_currency_item_metadata(item_metadata: dict, currency_item_id: int):
    async with BaseRepository.get_db_cursor() as cursor:
        query = """
            UPDATE currency_item
            SET item_metadata = %(item_metadata)s
            WHERE currency_item_id = %(currency_item_id)s
        """

        await cursor.execute(
            query,
            params={
                "item_metadata": json.dumps(item_metadata),
                "currency_item_id": currency_item_id,
            },
        )
