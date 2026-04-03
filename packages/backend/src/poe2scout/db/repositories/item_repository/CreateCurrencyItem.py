from typing import Optional
from ..base_repository import BaseRepository, scalar_as
from pydantic import BaseModel


class CreateCurrencyItemModel(BaseModel):
    itemId: int
    currencyCategoryId: int
    apiId: str
    text: str
    image: Optional[str] = None


class CreateCurrencyItem(BaseRepository):
    async def execute(self, currencyItem: CreateCurrencyItemModel) -> int:
        async with self.get_db_cursor(rowFactory=scalar_as(int)) as cursor:

            query = """
                INSERT INTO "CurrencyItem" ("itemId", "currencyCategoryId", "apiId", "text", "iconUrl")
                VALUES (%s, %s, %s, %s, %s)
                RETURNING "id"
            """

            await cursor.execute(
                query,
                (
                    currencyItem.itemId,
                    currencyItem.currencyCategoryId,
                    currencyItem.apiId,
                    currencyItem.text,
                    currencyItem.image,
                ),
            )

            return await anext(cursor)
