from typing import Tuple, Optional, List
from ..base_repository import BaseRepository
from pydantic import BaseModel

class BaseItem(BaseModel):
    id: int
    typeId: int
    iconUrl: Optional[str] = None
    itemMetadata: Optional[dict] = None


class GetAllBaseItems(BaseRepository):
    async def execute(self) -> List[BaseItem]:
        baseItem_query = """
            SELECT "id", "typeId", "iconUrl", "itemMetadata" FROM "BaseItem"
        """

        baseItems = await self.execute_query(
            baseItem_query)

        return [BaseItem(**baseItem) for baseItem in baseItems]
