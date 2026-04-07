from psycopg.rows import class_row

from ..base_repository import BaseRepository, RepositoryModel


class CategoryIcon(RepositoryModel):
    item_category_id: int
    api_id: str
    icon_url: str


async def get_category_icons(game_id: int) -> list[CategoryIcon]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(CategoryIcon)) as cursor:
        query = """
            SELECT gici.item_category_id
                 , ic.api_id
                 , gici.icon_url
              FROM game_item_category_icon AS gici
              JOIN item_category AS ic
                ON ic.item_category_id = gici.item_category_id
             WHERE gici.game_id = %(game_id)s
               AND ic.category_kind = 'item'
             ORDER BY gici.item_category_id
        """

        await cursor.execute(query, {"game_id": game_id})

        return await cursor.fetchall()
