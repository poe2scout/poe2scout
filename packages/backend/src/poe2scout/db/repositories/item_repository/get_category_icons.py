from psycopg.rows import class_row

from ..base_repository import BaseRepository, RepositoryModel


class CategoryIcon(RepositoryModel):
    api_id: str
    icon_url: str


async def get_category_icons(game_id: int) -> dict[str, str]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(CategoryIcon)) as cursor:
        query = """
            SELECT DISTINCT ON (ic.api_id)
                   ic.api_id,
                   ui.icon_url
              FROM unique_item AS ui
              JOIN item AS i ON i.item_id = ui.item_id
              JOIN base_item AS bi ON bi.base_item_id = i.base_item_id
              JOIN item_type AS it ON it.item_type_id = bi.item_type_id
              JOIN item_category AS ic ON ic.item_category_id = it.item_category_id
             WHERE bi.game_id = %(game_id)s
               AND NULLIF(ui.icon_url, '') IS NOT NULL
             ORDER BY ic.api_id, ui.item_id ASC
        """

        await cursor.execute(query, {"game_id": game_id})

        return {
            row.api_id: row.icon_url
            for row in await cursor.fetchall()
        }
