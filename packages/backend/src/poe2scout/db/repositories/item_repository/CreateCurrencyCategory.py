from ..base_repository import BaseRepository, scalar_as
from pydantic import BaseModel


class CreateCurrencyCategoryModel(BaseModel):
    id: str
    label: str


class CreateCurrencyCategory(BaseRepository):
    async def execute(self, currencyCategory: CreateCurrencyCategoryModel) -> int:
        async with self.get_db_cursor(rowFactory=scalar_as(int)) as cursor:
            query = """
                INSERT INTO "CurrencyCategory" ("apiId", "label")
                VALUES (%s, %s)
                RETURNING "id"
            """

            await cursor.execute(
                query, (currencyCategory.id, currencyCategory.label)
            )

            return await anext(cursor)
