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
    league_id: int, 
    realm_id: int,
    end_time: int, 
    limit: int
) -> GetCurrencyExchangeHistoryModel:
    async with BaseRepository.get_db_cursor(
        row_factory=class_row(GetCurrencyExchangeHistoryData)
    ) as cursor:
        query = """
                SELECT epoch,
                       market_cap,
                       volume
                  FROM currency_exchange_snapshot
                 WHERE league_id = %(league_id)s
                   AND realm_id = %(realm_id)s
                   AND epoch < %(end_time)s
                 ORDER BY
                       epoch DESC
                 LIMIT %(limit)s
        """

        params = {
            "league_id": league_id, 
            "realm_id": realm_id,
            "end_time": end_time, 
            "limit": limit + 1
        }

        await cursor.execute(query, params)

        records = await cursor.fetchall()

        has_more = False

        if len(records) > limit:
            has_more = True
            records.pop()

        return GetCurrencyExchangeHistoryModel(data=records, meta={"has_more": has_more})

