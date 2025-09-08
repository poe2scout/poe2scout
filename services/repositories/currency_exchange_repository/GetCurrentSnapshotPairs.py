from decimal import Decimal
from typing import List, Tuple, Optional
import json

from services.libs.models.CurrencyExchange.models import CurrencyExchangeSnapshotPair
from services.repositories.models import CurrencyItem
from ..base_repository import BaseRepository
from pydantic import BaseModel
from psycopg.rows import class_row

class PairDataDetails(BaseModel):
  ValueTraded: Decimal
  RelativePrice: Decimal
  StockValue: Decimal
  VolumeTraded: int
  HighestStock: int

class GetCurrentSnapshotPairModel(BaseModel):
  CurrencyExchangeSnapshotPairId: int
  CurrencyExchangeSnapshotId: int
  Volume: Decimal
  CurrencyOne: CurrencyItem
  CurrencyTwo: CurrencyItem
  CurrencyOneData: PairDataDetails
  CurrencyTwoData: PairDataDetails

class _FlatPairRow(BaseModel):
  CurrencyExchangeSnapshotPairId: int
  CurrencyExchangeSnapshotId: int
  Volume: Decimal
  c1_id: int
  c1_itemId: int
  c1_apiId: str
  c1_text: str
  c1_iconUrl: str
  c1_cat_id: int
  c1_cat_label: str
  c1_cat_apiId: str
  c2_id: int
  c2_itemId: int
  c2_apiId: str
  c2_text: str
  c2_iconUrl: str
  c2_cat_id: int
  c2_cat_label: str
  c2_cat_apiId: str
  c1_ValueTraded: Decimal
  c2_ValueTraded: Decimal
  c1_RelativePrice: Decimal
  c2_RelativePrice: Decimal
  c1_StockValue: Decimal
  c2_StockValue: Decimal
  c1_VolumeTraded: int
  c2_VolumeTraded: int
  c1_HighestStock: int
  c2_HighestStock: int

class GetCurrentSnapshotPairs(BaseRepository):
  async def execute(self, leagueId: int) -> List[GetCurrentSnapshotPairModel]:
    async with self.get_db_cursor(rowFactory=class_row(_FlatPairRow)) as cursor:

      query = """
WITH "CurrentSnapshotId" AS (
  SELECT "CurrencyExchangeSnapshotId"
    FROM "CurrencyExchangeSnapshot"
   WHERE "LeagueId" = %(leagueId)s
   ORDER BY "Epoch" DESC
   LIMIT 1
)
SELECT cesp."CurrencyExchangeSnapshotPairId",
       cesp."CurrencyExchangeSnapshotId",
       cesp."Volume",
       ci1."id" AS "c1_id",
       ci1."itemId" AS "c1_itemId",
       ci1."apiId" AS "c1_apiId",
       ci1."text" AS "c1_text",
       ci1."iconUrl" AS "c1_iconUrl",
       cc1."id" AS "c1_cat_id",
       cc1."label" AS "c1_cat_label",
       cc1."apiId" AS "c1_cat_apiId",
       ci2."id" AS "c2_id",
       ci2."itemId" AS "c2_itemId",
       ci2."apiId" AS "c2_apiId",
       ci2."text" AS "c2_text",
       ci2."iconUrl" AS "c2_iconUrl",
       cc2."id" AS "c2_cat_id",
       cc2."label" AS "c2_cat_label",
       cc2."apiId" AS "c2_cat_apiId",
       cespd1."ValueTraded" AS "c1_ValueTraded",
       cespd1."RelativePrice" AS "c1_RelativePrice",
       cespd1."StockValue" AS "c1_StockValue",
       cespd1."VolumeTraded" AS "c1_VolumeTraded",
       cespd1."HighestStock" AS "c1_HighestStock",
       cespd2."ValueTraded" AS "c2_ValueTraded",
       cespd2."RelativePrice" AS "c2_RelativePrice",
       cespd2."StockValue" AS "c2_StockValue",
       cespd2."VolumeTraded" AS "c2_VolumeTraded",
       cespd2."HighestStock" AS "c2_HighestStock"
  FROM "CurrencyExchangeSnapshotPair" AS cesp
  JOIN "CurrencyItem" AS ci1 ON cesp."CurrencyOneId" = ci1."id"
  JOIN "CurrencyCategory" AS cc1 ON ci1."currencyCategoryId" = cc1."id"
  JOIN "CurrencyItem" AS ci2 ON cesp."CurrencyTwoId" = ci2."id"
  JOIN "CurrencyCategory" AS cc2 ON ci2."currencyCategoryId" = cc2."id"
  JOIN "CurrencyExchangeSnapshotPairData" AS cespd1 ON cespd1."CurrencyExchangeSnapshotPairId" = cesp."CurrencyExchangeSnapshotPairId" AND cespd1."CurrencyId" = cesp."CurrencyOneId"
  JOIN "CurrencyExchangeSnapshotPairData" AS cespd2 ON cespd2."CurrencyExchangeSnapshotPairId" = cesp."CurrencyExchangeSnapshotPairId" AND cespd2."CurrencyId" = cesp."CurrencyTwoId"
 WHERE cesp."CurrencyExchangeSnapshotId" IN (SELECT "CurrencyExchangeSnapshotId" FROM "CurrentSnapshotId");
      """ 

      params = {
          "leagueId": leagueId
      }

      await cursor.execute(query, params)

      flat_results = await cursor.fetchall()

      structured_results: List[GetCurrentSnapshotPairModel] = []
      for row in flat_results:
        currency_one = CurrencyItem.model_construct(
          id=row.c1_id,
          itemId=row.c1_itemId,
          apiId=row.c1_apiId,
          text=row.c1_text,
          iconUrl=row.c1_iconUrl,
          currencyCategoryId=row.c1_cat_id,
          categoryApiId=row.c1_cat_apiId
        )
        currency_two = CurrencyItem.model_construct(
          id=row.c2_id,
          itemId=row.c2_itemId,
          apiId=row.c2_apiId,
          text=row.c2_text,
          iconUrl=row.c2_iconUrl,
          currencyCategoryId=row.c2_cat_id,
          categoryApiId=row.c2_cat_apiId
        )
        c1_data = PairDataDetails.model_construct(
          ValueTraded=row.c1_ValueTraded,
          RelativePrice=row.c1_RelativePrice,
          StockValue=row.c1_StockValue,
          VolumeTraded=row.c1_VolumeTraded,
          HighestStock=row.c1_HighestStock
        )
        c2_data = PairDataDetails.model_construct(
          ValueTraded=row.c2_ValueTraded,
          RelativePrice=row.c2_RelativePrice,
          StockValue=row.c2_StockValue,
          VolumeTraded=row.c2_VolumeTraded,
          HighestStock=row.c2_HighestStock
        )
        pair = GetCurrentSnapshotPairModel.model_construct(
          CurrencyExchangeSnapshotPairId=row.CurrencyExchangeSnapshotPairId,
          CurrencyExchangeSnapshotId=row.CurrencyExchangeSnapshotId,
          Volume=row.Volume,
          CurrencyOne=currency_one,
          CurrencyTwo=currency_two,
          CurrencyOneData=c1_data,
          CurrencyTwoData=c2_data
        )
        structured_results.append(pair)
      
      return structured_results  
