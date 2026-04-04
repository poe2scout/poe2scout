from psycopg.rows import class_row

from ..base_repository import BaseRepository, RepositoryModel


class GetCurrencyExchangeHistoryData(RepositoryModel):
    epoch: int
    market_cap: float
    volume: float


class GetCurrencyExchangeHistoryModel(RepositoryModel):
    data: list[GetCurrencyExchangeHistoryData]
    meta: dict[str, bool]


async def get_currency_exchange_history(
    league_id: int, end_time: int, limit: int
) -> GetCurrencyExchangeHistoryModel:
    async with BaseRepository.get_db_cursor(
        row_factory=class_row(GetCurrencyExchangeHistoryData)
    ) as cursor:
        query = """
                SELECT "Epoch" AS "epoch",
                       "MarketCap" AS "market_cap",
                       "Volume" AS "volume"
                  FROM "CurrencyExchangeSnapshot"
                 WHERE "LeagueId" = %(league_id)s
                       AND "Epoch" < %(end_time)s
                 ORDER BY
                       "Epoch" DESC
                 LIMIT %(limit)s
        """

        params = {"league_id": league_id, "end_time": end_time, "limit": limit + 1}

        await cursor.execute(query, params)

        records = await cursor.fetchall()

        has_more = False

        if len(records) > limit:
            has_more = True
            records.pop()

        return GetCurrencyExchangeHistoryModel(data=records, meta={"has_more": has_more})

