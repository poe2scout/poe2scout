from psycopg.rows import class_row

from ..base_repository import BaseRepository, RepositoryModel


class CategoryIcon(RepositoryModel):
    api_id: str
    icon_url: str


async def get_category_icons(game_id: int) -> dict[str, str]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(CategoryIcon)) as cursor:
        query = """
            SELECT DISTINCT ON (cc.api_id)
                   cc.api_id,
                   COALESCE(NULLIF(ci.icon_url, ''), NULLIF(bi.icon_url, '')) AS icon_url
              FROM currency_item AS ci
              JOIN currency_category AS cc ON cc.currency_category_id = ci.currency_category_id
              JOIN item AS i ON i.item_id = ci.item_id
              JOIN base_item AS bi ON bi.base_item_id = i.base_item_id
             WHERE bi.game_id = %(game_id)s
               AND COALESCE(NULLIF(ci.icon_url, ''), NULLIF(bi.icon_url, '')) IS NOT NULL
             ORDER BY cc.api_id, ci.item_id ASC
        """

        await cursor.execute(query, {"game_id": game_id})

        return {
            row.api_id: row.icon_url
            for row in await cursor.fetchall()
        }
