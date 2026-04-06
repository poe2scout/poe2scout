from typing import Optional

from poe2scout.integrations.poe.currency_exchange_models import CurrencyExchangeSnapshot

from ..base_repository import BaseRepository


async def create_snapshot(snapshot: CurrencyExchangeSnapshot) -> Optional[int]:
    if not snapshot.pairs:
        async with BaseRepository.get_db_cursor() as cursor:
            query = """
INSERT INTO currency_exchange_snapshot(epoch, league_id, realm_id, volume, market_cap)
VALUES(%(epoch)s, %(league_id)s, %(realm_id)s, %(volume)s, %(market_cap)s)
RETURNING currency_exchange_snapshot_id
            """
            params = {
                "epoch": snapshot.epoch,
                "league_id": snapshot.league_id,
                "realm_id": snapshot.realm_id,
                "volume": snapshot.volume,
                "market_cap": snapshot.market_cap,
            }
            await cursor.execute(query, params)
            result = await cursor.fetchone()
            return result["currency_exchange_snapshot_id"] if result else None

    pair_params = {
        "c1_ids": [pair.currency_one_item_id for pair in snapshot.pairs],
        "c2_ids": [pair.currency_two_item_id for pair in snapshot.pairs],
        "volumes": [pair.volume for pair in snapshot.pairs],
        "c1_val_traded": [pair.currency_one_data.value_traded for pair in snapshot.pairs],
        "c1_vol_traded": [pair.currency_one_data.volume_traded for pair in snapshot.pairs],
        "c1_stock": [pair.currency_one_data.highest_stock for pair in snapshot.pairs],
        "c1_price": [pair.currency_one_data.relative_price for pair in snapshot.pairs],
        "c1_stock_value": [pair.currency_one_data.stock_value for pair in snapshot.pairs],
        "c2_val_traded": [pair.currency_two_data.value_traded for pair in snapshot.pairs],
        "c2_vol_traded": [pair.currency_two_data.volume_traded for pair in snapshot.pairs],
        "c2_stock": [pair.currency_two_data.highest_stock for pair in snapshot.pairs],
        "c2_price": [pair.currency_two_data.relative_price for pair in snapshot.pairs],
        "c2_stock_value": [pair.currency_two_data.stock_value for pair in snapshot.pairs],
    }

    final_params = {
        "epoch": snapshot.epoch,
        "league_id": snapshot.league_id,
        "realm_id": snapshot.realm_id,
        "volume": snapshot.volume,
        "market_cap": snapshot.market_cap,
        **pair_params,
    }

    async with BaseRepository.get_db_cursor() as cursor:
        query = """
WITH snapshot_insert AS (
    INSERT INTO currency_exchange_snapshot(epoch, league_id, realm_id, volume, market_cap)
    VALUES (%(epoch)s, %(league_id)s, %(realm_id)s, %(volume)s, %(market_cap)s)
    RETURNING currency_exchange_snapshot_id
),
pair_data_unnested AS (
    SELECT
        row_number() OVER () as rn,
        c1_id, c2_id, volume,
        c1_val_traded, c1_vol_traded, c1_stock, c1_price, c1_stock_value,
        c2_val_traded, c2_vol_traded, c2_stock, c2_price, c2_stock_value
    FROM unnest(
        %(c1_ids)s::integer[],
        %(c2_ids)s::integer[],
        %(volumes)s::decimal[],
        %(c1_val_traded)s::decimal[],
        %(c1_vol_traded)s::bigint[],
        %(c1_stock)s::bigint[],
        %(c1_price)s::decimal[],
        %(c1_stock_value)s::decimal[],
        %(c2_val_traded)s::decimal[],
        %(c2_vol_traded)s::bigint[],
        %(c2_stock)s::bigint[],
        %(c2_price)s::decimal[],
        %(c2_stock_value)s::decimal[]
    ) AS t(
        c1_id, c2_id, volume,
        c1_val_traded, c1_vol_traded, c1_stock, c1_price, c1_stock_value,
        c2_val_traded, c2_vol_traded, c2_stock, c2_price, c2_stock_value
    )
),
pair_insert AS (
    INSERT INTO currency_exchange_snapshot_pair (
        currency_exchange_snapshot_id, currency_one_item_id, currency_two_item_id, volume
    )
    SELECT
        (SELECT currency_exchange_snapshot_id FROM snapshot_insert),
        pdu.c1_id,
        pdu.c2_id,
        pdu.volume
    FROM pair_data_unnested AS pdu
    RETURNING currency_exchange_snapshot_pair_id, currency_one_item_id, currency_two_item_id
),
pair_data_to_insert AS (
    SELECT
        pi.currency_exchange_snapshot_pair_id,
        pdu.c1_id AS item_id,
        pdu.c1_val_traded AS value_traded,
        pdu.c1_price AS relative_price,
        pdu.c1_vol_traded AS volume_traded,
        pdu.c1_stock AS highest_stock,
        pdu.c1_stock_value AS stock_value
    FROM pair_insert AS pi
    JOIN pair_data_unnested AS pdu ON pi.currency_one_item_id = pdu.c1_id
                                  AND pi.currency_two_item_id = pdu.c2_id
    UNION ALL
    SELECT
        pi.currency_exchange_snapshot_pair_id,
        pdu.c2_id,
        pdu.c2_val_traded,
        pdu.c2_price,
        pdu.c2_vol_traded,
        pdu.c2_stock,
        pdu.c2_stock_value
    FROM pair_insert AS pi
    JOIN pair_data_unnested AS pdu ON pi.currency_one_item_id = pdu.c1_id
                                  AND pi.currency_two_item_id = pdu.c2_id
),
final_insert AS (
    INSERT INTO currency_exchange_snapshot_pair_data (
        currency_exchange_snapshot_pair_id, item_id, value_traded,
        relative_price, volume_traded, highest_stock, stock_value
    )
    SELECT * FROM pair_data_to_insert
    RETURNING 1
)
SELECT currency_exchange_snapshot_id FROM snapshot_insert;
        """
        await cursor.execute(query, final_params)
        return (await cursor.fetchall())[0]["currency_exchange_snapshot_id"]
