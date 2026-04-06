from typing import Optional

from psycopg.rows import class_row

from ..base_repository import BaseRepository, RepositoryModel


class BaseItem(RepositoryModel):
    base_item_id: int
    item_type_id: int
    game_id: int
    icon_url: Optional[str] = None
    item_metadata: Optional[dict] = None


async def get_all_base_items(game_id: int) -> list[BaseItem]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(BaseItem)) as cursor:
        query = """
            SELECT bi.base_item_id
                 , bi.item_type_id
                 , bi.icon_url
                 , bi.item_metadata
                 , bi.game_id
              FROM base_item as bi
             WHERE bi.game_id = %(game_id)s
        """

        params = {
            "game_id": game_id
        }

        await cursor.execute(query, params)

        return await cursor.fetchall()