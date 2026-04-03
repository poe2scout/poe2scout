from psycopg.rows import class_row
from ..base_repository import BaseRepository
from pydantic import BaseModel

# Define the structure for each search option returned


class SearchOption(BaseModel):
    display_name: str
    category: str
    identifier: str


class GetSearchOptions(BaseRepository):
    """
    Fetches a list of all searchable items (Unique and Currency)
    for use in frontend autocomplete.
    """

    async def execute(self) -> list[SearchOption]:
        async with self.get_db_cursor(
            rowFactory=class_row(SearchOption)
        ) as cursor:
            query = """
                SELECT
                    ui.name AS display_name,  -- UniqueItem.name
                    ic."apiId" AS category,     -- ItemType.value (joined)
                    ui.name AS identifier     -- UniqueItem.name (used for search)
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
