from decimal import Decimal

from psycopg.rows import class_row

from ..base_repository import BaseRepository, RepositoryModel


class GetCurrencyExchangeModel(RepositoryModel):
    epoch: int
    volume: Decimal
    market_cap: Decimal


async def get_currency_exchange(league_id: int) -> GetCurrencyExchangeModel | None:
    async with BaseRepository.get_db_cursor(
        row_factory=class_row(GetCurrencyExchangeModel)
    ) as cursor:
        query = """
            SELECT epoch,
                   volume,
                   market_cap
              FROM currency_exchange_snapshot
             WHERE league_id = %(league_id)s
             ORDER BY epoch DESC
             LIMIT 1
        """

        params = {"league_id": league_id}

        await cursor.execute(query, params)

        return await cursor.fetchone()
