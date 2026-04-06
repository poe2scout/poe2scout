from psycopg.rows import class_row

from ..base_repository import BaseRepository, RepositoryModel


class Item(RepositoryModel):
    item_id: int
    base_item_id: int
    item_type: str


async def get_all_items(game_id: int) -> list[Item]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(Item)) as cursor:
        query = """
            SELECT item_id
                 , base_item_id
                 , item_type
            FROM item i
            JOIN base_item bi ON i.base_item_id = bi.base_item_id
            WHERE bi.game_id = %(game_id)s
        """

        params = {
            "game_id": game_id
        }

        await cursor.execute(query, params)

        return await cursor.fetchall()
