from decimal import Decimal
from typing import List
from ..base_repository import BaseRepository
from pydantic import BaseModel
from psycopg.rows import class_row

class PairDataDetails(BaseModel):
    CurrencyApiId: str
    ValueTraded: Decimal
    RelativePrice: Decimal
    StockValue: Decimal
    VolumeTraded: int
    HighestStock: int

class PairData(BaseModel):
    CurrencyOneData: PairDataDetails
    CurrencyTwoData: PairDataDetails

class GetCurrentSnapshotPairModel(BaseModel):
    Epoch: int
    Data: PairData

class GetPairHistoryModel(BaseModel):
    History: List[GetCurrentSnapshotPairModel]
    Meta: dict[str, object]

class _pair_history_db_row(BaseModel):
    Epoch: int
    C1_CurrencyApiId: str
    C1_ValueTraded: Decimal
    C1_RelativePrice: Decimal
    C1_StockValue: Decimal
    C1_VolumeTraded: int
    C1_HighestStock: int
    C2_CurrencyApiId: str
    C2_ValueTraded: Decimal
    C2_RelativePrice: Decimal
    C2_StockValue: Decimal
    C2_VolumeTraded: int
    C2_HighestStock: int

   

class GetPairHistory(BaseRepository):
    async def execute(self, currencyOneApiId: str, currencyTwoApiId: str, leagueId: int, endTime: int, limit: int):
        async with self.get_db_cursor(rowFactory=class_row(_pair_history_db_row)) as cursor:
            query = """
SELECT ces."Epoch", 
	   c1."apiId" AS "C1_CurrencyApiId", 
	   cespd1."ValueTraded" AS "C1_ValueTraded",
	   cespd1."RelativePrice" AS "C1_RelativePrice",
	   cespd1."StockValue" AS "C1_StockValue",
	   cespd1."VolumeTraded" AS "C1_VolumeTraded",
	   cespd1."HighestStock" AS "C1_HighestStock",
	   c2."apiId" AS "C2_CurrencyApiId",
	   cespd2."ValueTraded" AS "C2_ValueTraded",
	   cespd2."RelativePrice" AS "C2_RelativePrice",
	   cespd2."StockValue" AS "C2_StockValue",
	   cespd2."VolumeTraded" AS "C2_VolumeTraded",
	   cespd2."HighestStock" AS "C2_HighestStock"
  FROM "CurrencyExchangeSnapshot" AS ces
  JOIN "CurrencyExchangeSnapshotPair" AS cesp ON cesp."CurrencyExchangeSnapshotId" = ces."CurrencyExchangeSnapshotId"
  JOIN "CurrencyItem" AS c1 ON cesp."CurrencyOneId" = c1."itemId"
  JOIN "CurrencyItem" AS c2 ON cesp."CurrencyTwoId" = c2."itemId"
  JOIN "CurrencyExchangeSnapshotPairData" AS cespd1 ON cespd1."CurrencyExchangeSnapshotPairId" = cesp."CurrencyExchangeSnapshotPairId" AND cespd1."CurrencyId" = cesp."CurrencyOneId"
  JOIN "CurrencyExchangeSnapshotPairData" AS cespd2 ON cespd2."CurrencyExchangeSnapshotPairId" = cesp."CurrencyExchangeSnapshotPairId" AND cespd2."CurrencyId" = cesp."CurrencyTwoId"
 WHERE ((cesp."CurrencyOneId" = 291 AND cesp."CurrencyTwoId" = 290) 
        OR (cesp."CurrencyOneId" = 290 AND cesp."CurrencyTwoId" = 291))
   AND ces."LeagueId" = 5
ORDER BY ces."Epoch" DESC
LIMIT %(limit)s 
            """

            params = {
                "currencyOneApiId": currencyOneApiId,
                "currencyTwoApiId": currencyTwoApiId,
                "leagueId": leagueId,
                "endTime": endTime,
                "limit": limit+1
            }

            await cursor.execute(query, params)
            
            records = await cursor.fetchall() 

            hasMore = False

            if (len(records) > limit):
                hasMore = True
                records.pop()
            
            records.reverse()
            
            returnList: List[GetCurrentSnapshotPairModel] = []
            for record in records:
                C1PairDataDetails = PairDataDetails.model_construct(
                    CurrencyApiId=record.C1_CurrencyApiId,
                    HighestStock=record.C1_HighestStock,
                    RelativePrice=record.C1_RelativePrice,
                    StockValue=record.C1_StockValue,
                    Valuetraded=record.C1_ValueTraded,
                    VolumeTraded=record.C1_VolumeTraded)
                C2PairDataDetails = PairDataDetails.model_construct(
                    CurrencyApiId=record.C2_CurrencyApiId,
                    HighestStock=record.C2_HighestStock,
                    RelativePrice=record.C2_RelativePrice,
                    StockValue=record.C2_StockValue,
                    Valuetraded=record.C2_ValueTraded,
                    VolumeTraded=record.C2_VolumeTraded)
                RecordPairData = PairData.model_construct(CurrencyOneData=C1PairDataDetails, CurrencyTwoData=C2PairDataDetails)
                RecordModel = GetCurrentSnapshotPairModel.model_construct(Epoch=record.Epoch, Data=RecordPairData)
                returnList.append(RecordModel)

            return GetPairHistoryModel(History=returnList, Meta={"hasMore": hasMore})
