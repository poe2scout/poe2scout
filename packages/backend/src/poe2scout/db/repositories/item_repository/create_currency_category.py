from ..base_repository import BaseRepository, RepositoryModel, scalar_as


class CreateCurrencyCategoryModel(RepositoryModel):
    id: str
    label: str


async def create_currency_category(currency_category: CreateCurrencyCategoryModel) -> int:
    async with BaseRepository.get_db_cursor(row_factory=scalar_as(int)) as cursor:
        query = """
            INSERT INTO "CurrencyCategory" ("apiId", "label")
            VALUES (%s, %s)
            RETURNING "id"
        """

        await cursor.execute(query, (currency_category.id, currency_category.label))

        return await anext(cursor)


class CreateCurrencyCategory(BaseRepository):
    async def execute(self, currency_category: CreateCurrencyCategoryModel) -> int:
        return await create_currency_category(currency_category)
