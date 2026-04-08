from psycopg.rows import class_row

from ..base_repository import BaseRepository, RepositoryModel


class BridgeCurrency(RepositoryModel):
    item_id: int
    currency_item_id: int
    api_id: str
    text: str
    bridge_rank: int


async def get_bridge_currencies(game_id: int) -> list[BridgeCurrency]:
    async with BaseRepository.get_db_cursor(row_factory=class_row(BridgeCurrency)) as cursor:
        query = """
            SELECT ci.item_id,
                   ci.currency_item_id,
                   ci.api_id,
                   ci.text,
                   gcb.bridge_rank
              FROM game_currency_bridge AS gcb
              JOIN currency_item AS ci
                ON ci.currency_item_id = gcb.currency_item_id
              JOIN item AS i
                ON i.item_id = ci.item_id
              JOIN base_item AS bi
                ON bi.base_item_id = i.base_item_id
             WHERE gcb.game_id = %(game_id)s
               AND bi.game_id = %(game_id)s
             ORDER BY gcb.bridge_rank ASC
        """
        params = {"game_id": game_id}

        await cursor.execute(query, params)
        return await cursor.fetchall()
