from typing import Optional

from ..base_repository import BaseRepository, RepositoryModel, scalar_as


class CreateCurrencyItemModel(RepositoryModel):
    item_id: int
    currency_category_id: int
    api_id: str
    text: str
    image: Optional[str] = None


async def create_currency_item(currency_item: CreateCurrencyItemModel) -> int:
    async with BaseRepository.get_db_cursor(row_factory=scalar_as(int)) as cursor:
        query = """
            INSERT INTO "CurrencyItem" ("itemId", "currencyCategoryId", "apiId", "text", "iconUrl")
            VALUES (%s, %s, %s, %s, %s)
            RETURNING "id"
        """

        await cursor.execute(
            query,
            (
                currency_item.item_id,
                currency_item.currency_category_id,
                currency_item.api_id,
                currency_item.text,
                currency_item.image,
            ),
        )

        return await anext(cursor)


class CreateCurrencyItem(BaseRepository):
    async def execute(self, currency_item: CreateCurrencyItemModel) -> int:
        return await create_currency_item(currency_item)
