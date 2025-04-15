from typing import Tuple, Optional, List
from ..base_repository import BaseRepository
from pydantic import BaseModel

class UniqueBaseItem(BaseModel):
    id: int
    iconUrl: Optional[str] = None
    itemMetadata: Optional[dict] = None
    itemId: int
    name: str
    apiId: str

class GetAllUniqueBaseItems(BaseRepository):
    async def execute(self) -> List[UniqueBaseItem]:
        baseItem_query = """
                        WITH unique_ids AS (
                            SELECT DISTINCT "baseItemId" FROM "Item"
                            WHERE "itemType" = 'unique'
                        ),
                        valid_items AS (
                            SELECT * FROM "Item"
                            WHERE "itemType" = 'base'
                        )
                        SELECT 
                            "bi"."id", 
                            "bi"."iconUrl", 
                            "bi"."itemMetadata", 
                            "i".id as "itemId", 
                            "it"."value" as name, 
                            ic."apiId" 
                        FROM "BaseItem" as bi
                        JOIN valid_items as i ON "bi"."id" = "i"."baseItemId" 
                        JOIN "ItemType" as it ON "bi"."typeId" = "it"."id"
                        JOIN "ItemCategory" as ic on it."categoryId" = ic.id
                        WHERE "bi"."id" IN (SELECT "baseItemId" FROM unique_ids)
        """

        baseItems = await self.execute_query(
            baseItem_query)
        
        print(len(baseItems))
        return [UniqueBaseItem(**baseItem) for baseItem in baseItems]
