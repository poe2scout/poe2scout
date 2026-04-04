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
                SELECT ib.id as "base_item_id", ui."itemId"
                FROM "Item" as ib
                JOIN "BaseItem" as bi on ib."baseItemId" = bi.id
                JOIN "Item" ON "Item"."baseItemId" = bi.id AND "Item"."itemType" = 'unique'
                JOIN "UniqueItem" as ui ON ui."itemId" = "Item".id
                WHERE ib.id = ANY(%s) AND ui."isChanceable" = TRUE
            ),
            latest_prices AS (
                SELECT DISTINCT ON (pl."itemId")
                    ui."base_item_id",
                    pl."itemId",
                    pl.price
                FROM "PriceLog" as pl
                JOIN unique_item_ids ui ON ui."itemId" = pl."itemId"
                WHERE pl."leagueId" = %s
                ORDER BY pl."itemId", pl."createdAt" DESC
            )
            SELECT "base_item_id"
                , AVG(price) as average_price
            FROM latest_prices
            GROUP BY "base_item_id";
        """

        await cursor.execute(query, (item_ids, league_id))
        results = {row.base_item_id: row.average_price for row in await cursor.fetchall()}

        return {item_id: results.get(item_id) for item_id in item_ids}


class GetAverageUniquePrice(BaseRepository):
    async def execute(self, item_ids: list[int], league_id: int) -> dict[int, float | None]:
        return await get_average_unique_price(item_ids, league_id)
