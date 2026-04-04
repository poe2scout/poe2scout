from psycopg.rows import class_row

from ..base_repository import BaseRepository, RepositoryModel


class SearchOption(RepositoryModel):
    display_name: str
    category: str
    identifier: str


async def get_search_options() -> list[SearchOption]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(SearchOption)) as cursor:
        query = """
            SELECT
                ui.name AS display_name,
                ic."apiId" AS category,
                ui.name AS identifier
            FROM "UniqueItem" ui
            JOIN "Item" i ON ui."itemId" = i.id
            JOIN "BaseItem" bi ON i."baseItemId" = bi.id
            JOIN "ItemType" it ON bi."typeId" = it.id
            JOIN "ItemCategory" ic ON ic.id = it."categoryId"
            WHERE i."itemType" = 'unique'

            UNION ALL

            SELECT
                ci.text AS display_name,
                LOWER(COALESCE(cc."apiId", '')) AS category,
                ci.text AS identifier
            FROM "CurrencyItem" ci
            JOIN "Item" i ON ci."itemId" = i.id
            JOIN "CurrencyCategory" cc ON cc.id = ci."currencyCategoryId"
            WHERE i."itemType" = 'currency';
        """
        await cursor.execute(query)

        return await cursor.fetchall()