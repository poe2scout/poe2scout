from decimal import Decimal

from psycopg.rows import class_row

from poe2scout.db.repositories.models import CurrencyItem

from ..base_repository import BaseRepository, RepositoryModel


class PairDataDetails(RepositoryModel):
    value_traded: Decimal
    relative_price: Decimal
    stock_value: Decimal
    volume_traded: int
    highest_stock: int


class GetCurrentSnapshotPairModel(RepositoryModel):
    currency_exchange_snapshot_pair_id: int
    currency_exchange_snapshot_id: int
    volume: Decimal
    currency_one: CurrencyItem
    currency_two: CurrencyItem
    currency_one_data: PairDataDetails
    currency_two_data: PairDataDetails


class _FlatPairRow(RepositoryModel):
    currency_exchange_snapshot_pair_id: int
    currency_exchange_snapshot_id: int
    volume: Decimal
    c1_id: int
    c1_item_id: int
    c1_api_id: str
    c1_text: str
    c1_icon_url: str
    c1_cat_id: int
    c1_cat_label: str
    c1_cat_api_id: str
    c2_id: int
    c2_item_id: int
    c2_api_id: str
    c2_text: str
    c2_icon_url: str
    c2_cat_id: int
    c2_cat_label: str
    c2_cat_api_id: str
    c1_value_traded: Decimal
    c2_value_traded: Decimal
    c1_relative_price: Decimal
    c2_relative_price: Decimal
    c1_stock_value: Decimal
    c2_stock_value: Decimal
    c1_volume_traded: int
    c2_volume_traded: int
    c1_highest_stock: int
    c2_highest_stock: int


async def get_current_snapshot_pairs(league_id: int) -> list[GetCurrentSnapshotPairModel]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(_FlatPairRow)) as cursor:
        query = """
WITH "CurrentSnapshotId" AS (
  SELECT "CurrencyExchangeSnapshotId"
    FROM "CurrencyExchangeSnapshot"
   WHERE "LeagueId" = %(league_id)s
   ORDER BY "Epoch" DESC
   LIMIT 1
)
SELECT cesp."CurrencyExchangeSnapshotPairId" AS "currency_exchange_snapshot_pair_id",
       cesp."CurrencyExchangeSnapshotId" AS "currency_exchange_snapshot_id",
       cesp."Volume" AS "volume",
       ci1."id" AS "c1_id",
       ci1."itemId" AS "c1_item_id",
       ci1."apiId" AS "c1_api_id",
       ci1."text" AS "c1_text",
       ci1."iconUrl" AS "c1_icon_url",
       cc1."id" AS "c1_cat_id",
       cc1."label" AS "c1_cat_label",
       cc1."apiId" AS "c1_cat_api_id",
       ci2."id" AS "c2_id",
       ci2."itemId" AS "c2_item_id",
       ci2."apiId" AS "c2_api_id",
       ci2."text" AS "c2_text",
       ci2."iconUrl" AS "c2_icon_url",
       cc2."id" AS "c2_cat_id",
       cc2."label" AS "c2_cat_label",
       cc2."apiId" AS "c2_cat_api_id",
       cespd1."ValueTraded" AS "c1_value_traded",
       cespd1."RelativePrice" AS "c1_relative_price",
       cespd1."StockValue" AS "c1_stock_value",
       cespd1."VolumeTraded" AS "c1_volume_traded",
       cespd1."HighestStock" AS "c1_highest_stock",
       cespd2."ValueTraded" AS "c2_value_traded",
       cespd2."RelativePrice" AS "c2_relative_price",
       cespd2."StockValue" AS "c2_stock_value",
       cespd2."VolumeTraded" AS "c2_volume_traded",
       cespd2."HighestStock" AS "c2_highest_stock"
  FROM "CurrencyExchangeSnapshotPair" AS cesp
  JOIN "CurrencyItem" AS ci1 ON cesp."CurrencyOneId" = ci1."itemId"
  JOIN "CurrencyCategory" AS cc1 ON ci1."currencyCategoryId" = cc1."id"
  JOIN "CurrencyItem" AS ci2 ON cesp."CurrencyTwoId" = ci2."itemId"
  JOIN "CurrencyCategory" AS cc2 ON ci2."currencyCategoryId" = cc2."id"
  JOIN "CurrencyExchangeSnapshotPairData" AS cespd1
        ON cespd1."CurrencyExchangeSnapshotPairId" = cesp."CurrencyExchangeSnapshotPairId"
        AND cespd1."CurrencyId" = cesp."CurrencyOneId"
  JOIN "CurrencyExchangeSnapshotPairData" AS cespd2
        ON cespd2."CurrencyExchangeSnapshotPairId" = cesp."CurrencyExchangeSnapshotPairId"
        AND cespd2."CurrencyId" = cesp."CurrencyTwoId"
 WHERE cesp."CurrencyExchangeSnapshotId" IN (SELECT "CurrencyExchangeSnapshotId"
                                               FROM "CurrentSnapshotId");
      """

        params = {"league_id": league_id}

        await cursor.execute(query, params)

        flat_results = await cursor.fetchall()

        structured_results: list[GetCurrentSnapshotPairModel] = []
        for row in flat_results:
            currency_one = CurrencyItem.model_construct(
                id=row.c1_id,
                item_id=row.c1_item_id,
                api_id=row.c1_api_id,
                text=row.c1_text,
                icon_url=row.c1_icon_url,
                currency_category_id=row.c1_cat_id,
                category_api_id=row.c1_cat_api_id,
            )
            currency_two = CurrencyItem.model_construct(
                id=row.c2_id,
                item_id=row.c2_item_id,
                api_id=row.c2_api_id,
                text=row.c2_text,
                icon_url=row.c2_icon_url,
                currency_category_id=row.c2_cat_id,
                category_api_id=row.c2_cat_api_id,
            )
            c1_data = PairDataDetails.model_construct(
                value_traded=row.c1_value_traded,
                relative_price=row.c1_relative_price,
                stock_value=row.c1_stock_value,
                volume_traded=row.c1_volume_traded,
                highest_stock=row.c1_highest_stock,
            )
            c2_data = PairDataDetails.model_construct(
                value_traded=row.c2_value_traded,
                relative_price=row.c2_relative_price,
                stock_value=row.c2_stock_value,
                volume_traded=row.c2_volume_traded,
                highest_stock=row.c2_highest_stock,
            )
            pair = GetCurrentSnapshotPairModel.model_construct(
                currency_exchange_snapshot_pair_id=row.currency_exchange_snapshot_pair_id,
                currency_exchange_snapshot_id=row.currency_exchange_snapshot_id,
                volume=row.volume,
                currency_one=currency_one,
                currency_two=currency_two,
                currency_one_data=c1_data,
                currency_two_data=c2_data,
            )
            structured_results.append(pair)

        return structured_results
