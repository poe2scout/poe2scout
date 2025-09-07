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
    async def execute(self, currencyOneId: int, currencyTwoId: int, leagueId: int, endEpoch: int, limit: int):
        async with self.get_db_cursor(rowFactory=class_row(_pair_history_db_row)) as cursor:
            query = """
EXPLAIN ANALYSE (
    SELECT
        *
    FROM currency_exchange_history
    WHERE
        "LeagueId" = %(leagueId)s
        AND "Epoch" < %(endEpoch)s
        AND "CurrencyOneId" = %(currencyTwoId)s
        AND "CurrencyTwoId" = %(currencyOneId)s
    ORDER BY "Epoch" DESC
    LIMIT %(limit)s
)
UNION ALL
(
    SELECT
        *
    FROM currency_exchange_history
    WHERE
        "LeagueId" = %(leagueId)s
        AND "Epoch" < %(endEpoch)s
        AND "CurrencyOneId" = %(currencyOneId)s
        AND "CurrencyTwoId" = %(currencyTwoId)s
    ORDER BY "Epoch" DESC
    LIMIT %(limit)s
)
ORDER BY "Epoch" DESC
LIMIT %(limit)s;
            """

            params = {
                "currencyOneId": currencyOneId,
                "currencyTwoId": currencyTwoId,
                "leagueId": leagueId,
                "endEpoch": endEpoch,
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
