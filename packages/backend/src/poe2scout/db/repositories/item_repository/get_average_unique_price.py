from psycopg.rows import class_row

from ..base_repository import BaseRepository, RepositoryModel


class AverageUniquePrice(RepositoryModel):
    base_item_id: int
    average_price: float


async def get_average_unique_price(
    item_ids: list[int], league_id: int
) -> dict[int, float | None]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(AverageUniquePrice)) as cursor:
        query = """
            WITH unique_item_ids AS (
                SELECT ib.item_id AS base_item_id, ui.item_id
                FROM item as ib
                JOIN base_item as bi on ib.base_item_id = bi.base_item_id
                JOIN item ON item.base_item_id = bi.base_item_id AND item.item_type = 'unique'
                JOIN unique_item as ui ON ui.item_id = item.item_id
                WHERE ib.item_id = ANY(%s) AND ui.is_chanceable = TRUE
            ),
            latest_prices AS (
                SELECT DISTINCT ON (pl.item_id)
                    ui.base_item_id,
                    pl.item_id,
                    pl.price
                FROM price_log as pl
                JOIN unique_item_ids ui ON ui.item_id = pl.item_id
                WHERE pl.league_id = %s
                ORDER BY pl.item_id, pl.created_at DESC
            )
            SELECT base_item_id
                , AVG(price) as average_price
            FROM latest_prices
            GROUP BY base_item_id;
        """

        await cursor.execute(query, (item_ids, league_id))
        results = {row.base_item_id: row.average_price for row in await cursor.fetchall()}

        return {item_id: results.get(item_id) for item_id in item_ids}


class GetAverageUniquePrice(BaseRepository):
    async def execute(self, item_ids: list[int], league_id: int) -> dict[int, float | None]:
        return await get_average_unique_price(item_ids, league_id)
