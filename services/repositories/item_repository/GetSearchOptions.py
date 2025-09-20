from typing import List
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

    async def execute(self) -> List[SearchOption]:
        search_options_query = """
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
                ci.text AS display_name,   -- CurrencyItem.text
                LOWER(COALESCE(cc."apiId", '')) AS category,    -- Fixed string for navigation category
                ci.text AS identifier      -- CurrencyItem.text (used for search)
            FROM "CurrencyItem" ci
            JOIN "Item" i ON ci."itemId" = i.id
            JOIN "CurrencyCategory" cc ON cc.id = ci."currencyCategoryId"
            WHERE i."itemType" = 'currency';
        """

        # Execute the query - no parameters needed for this query
        results = await self.execute_query(search_options_query)

        # Map the raw results to the SearchOption model
        search_options = [SearchOption(**row) for row in results]

        return search_options
