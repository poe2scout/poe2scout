from dataclasses import dataclass
from enum import StrEnum
from typing import Optional

from ..base_repository import BaseRepository, RepositoryModel, scalar_as


class CreateCurrencyItemModel(RepositoryModel):
    item_id: int
    item_category_id: int
    api_id: str
    text: str
    image: Optional[str] = None


class CreateCurrencyItemError(StrEnum):
    INVALID_CATEGORY_KIND = "invalid_category_kind"


@dataclass(frozen=True)
class CreateCurrencyItemResult:
    ok: bool
    currency_item_id: int | None = None
    error: CreateCurrencyItemError | None = None


async def create_currency_item(
    currency_item: CreateCurrencyItemModel
) -> CreateCurrencyItemResult:
    async with BaseRepository.get_db_cursor(row_factory=scalar_as(bool)) as cursor:
        validation_query = """
            SELECT EXISTS(
                SELECT 1
                  FROM item_category
                 WHERE item_category_id = %s
                   AND category_kind = 'currency'
            )
        """

        await cursor.execute(validation_query, (currency_item.item_category_id,))
        is_valid_category = await anext(cursor)

        if not is_valid_category:
            return CreateCurrencyItemResult(
                ok=False,
                error=CreateCurrencyItemError.INVALID_CATEGORY_KIND,
            )

    async with BaseRepository.get_db_cursor(row_factory=scalar_as(int)) as cursor:
        insert_query = """
            INSERT INTO currency_item (item_id, item_category_id, api_id, text, icon_url)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING currency_item_id
        """

        await cursor.execute(
            insert_query,
            (
                currency_item.item_id,
                currency_item.item_category_id,
                currency_item.api_id,
                currency_item.text,
                currency_item.image,
            ),
        )

        return CreateCurrencyItemResult(
            ok=True,
            currency_item_id=await anext(cursor),
        )


class CreateCurrencyItem(BaseRepository):
    async def execute(
        self,
        currency_item: CreateCurrencyItemModel,
    ) -> CreateCurrencyItemResult:
        return await create_currency_item(currency_item)
