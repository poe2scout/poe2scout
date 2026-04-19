from ..base_repository import BaseRepository, scalar_as


async def get_items_in_current_league(league_id: int, realm_id: int) -> list[int]:
    async with BaseRepository.get_db_cursor(row_factory=scalar_as(int)) as cursor:
        query = """
WITH RECURSIVE distinct_items AS (
    (
        SELECT item_id 
        FROM price_log 
        WHERE league_id = %(league_id)s AND realm_id = %(realm_id)s 
        ORDER BY item_id 
        LIMIT 1
    )
    UNION ALL
    SELECT (
        SELECT item_id 
        FROM price_log 
        WHERE league_id = %(league_id)s AND realm_id = %(realm_id)s
          AND item_id > distinct_items.item_id 
        ORDER BY item_id 
        LIMIT 1
    )
    FROM distinct_items
    WHERE distinct_items.item_id IS NOT NULL
)
SELECT item_id 
FROM distinct_items
WHERE item_id IS NOT NULL
        """
        await cursor.execute(query, {"league_id": league_id, "realm_id": realm_id})

        return await cursor.fetchall()
