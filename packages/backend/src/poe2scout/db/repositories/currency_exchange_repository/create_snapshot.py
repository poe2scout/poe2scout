from typing import Optional

from poe2scout.integrations.poe.currency_exchange_models import CurrencyExchangeSnapshot

from ..base_repository import BaseRepository


async def create_snapshot(snapshot: CurrencyExchangeSnapshot) -> Optional[int]:
    if not snapshot.Pairs:
        async with BaseRepository.get_db_cursor() as cursor:
            query = """
INSERT INTO "CurrencyExchangeSnapshot"("Epoch", "LeagueId", "Volume", "MarketCap")
VALUES(%(Epoch)s, %(LeagueId)s, %(Volume)s, %(MarketCap)s)
RETURNING "CurrencyExchangeSnapshotId"
            """
            params = {
                "Epoch": snapshot.Epoch,
                "LeagueId": snapshot.LeagueId,
                "Volume": snapshot.Volume,
                "MarketCap": snapshot.MarketCap,
            }
            await cursor.execute(query, params)
            result = await cursor.fetchone()
            return result["CurrencyExchangeSnapshotId"] if result else None

    pair_params = {
        "c1_ids": [pair.CurrencyOneItemId for pair in snapshot.Pairs],
        "c2_ids": [pair.CurrencyTwoItemId for pair in snapshot.Pairs],
        "volumes": [pair.Volume for pair in snapshot.Pairs],
        "c1_val_traded": [pair.CurrencyOneData.ValueTraded for pair in snapshot.Pairs],
        "c1_vol_traded": [pair.CurrencyOneData.VolumeTraded for pair in snapshot.Pairs],
        "c1_stock": [pair.CurrencyOneData.HighestStock for pair in snapshot.Pairs],
        "c1_price": [pair.CurrencyOneData.RelativePrice for pair in snapshot.Pairs],
        "c1_stock_value": [pair.CurrencyOneData.StockValue for pair in snapshot.Pairs],
        "c2_val_traded": [pair.CurrencyTwoData.ValueTraded for pair in snapshot.Pairs],
        "c2_vol_traded": [pair.CurrencyTwoData.VolumeTraded for pair in snapshot.Pairs],
        "c2_stock": [pair.CurrencyTwoData.HighestStock for pair in snapshot.Pairs],
        "c2_price": [pair.CurrencyTwoData.RelativePrice for pair in snapshot.Pairs],
        "c2_stock_value": [pair.CurrencyTwoData.StockValue for pair in snapshot.Pairs],
    }

    final_params = {
        "Epoch": snapshot.Epoch,
        "LeagueId": snapshot.LeagueId,
        "Volume": snapshot.Volume,
        "MarketCap": snapshot.MarketCap,
        **pair_params,
    }

    async with BaseRepository.get_db_cursor() as cursor:
        query = """
WITH snapshot_insert AS (
    INSERT INTO "CurrencyExchangeSnapshot"("Epoch", "LeagueId", "Volume", "MarketCap")
    VALUES (%(Epoch)s, %(LeagueId)s, %(Volume)s, %(MarketCap)s)
    RETURNING "CurrencyExchangeSnapshotId"
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
    INSERT INTO "CurrencyExchangeSnapshotPair" (
        "CurrencyExchangeSnapshotId", "CurrencyOneId", "CurrencyTwoId", "Volume"
    )
    SELECT
        (SELECT "CurrencyExchangeSnapshotId" FROM snapshot_insert),
        pdu.c1_id,
        pdu.c2_id,
        pdu.volume
    FROM pair_data_unnested AS pdu
    RETURNING "CurrencyExchangeSnapshotPairId", "CurrencyOneId", "CurrencyTwoId"
),
pair_data_to_insert AS (
    SELECT
        pi."CurrencyExchangeSnapshotPairId",
        pdu.c1_id AS "CurrencyId",
        pdu.c1_val_traded AS "ValueTraded",
        pdu.c1_price AS "RelativePrice",
        pdu.c1_vol_traded AS "VolumeTraded",
        pdu.c1_stock AS "HighestStock",
        pdu.c1_stock_value AS "StockValue"
    FROM pair_insert AS pi
    JOIN pair_data_unnested AS pdu ON pi."CurrencyOneId" = pdu.c1_id
                                  AND pi."CurrencyTwoId" = pdu.c2_id
    UNION ALL
    SELECT
        pi."CurrencyExchangeSnapshotPairId",
        pdu.c2_id,
        pdu.c2_val_traded,
        pdu.c2_price,
        pdu.c2_vol_traded,
        pdu.c2_stock,
        pdu.c2_stock_value
    FROM pair_insert AS pi
    JOIN pair_data_unnested AS pdu ON pi."CurrencyOneId" = pdu.c1_id
                                  AND pi."CurrencyTwoId" = pdu.c2_id
),
final_insert AS (
    INSERT INTO "CurrencyExchangeSnapshotPairData" (
        "CurrencyExchangeSnapshotPairId", "CurrencyId", "ValueTraded",
        "RelativePrice", "VolumeTraded", "HighestStock", "StockValue"
    )
    SELECT * FROM pair_data_to_insert
    RETURNING 1
)
SELECT "CurrencyExchangeSnapshotId" FROM snapshot_insert;
        """
        await cursor.execute(query, final_params)
        return (await cursor.fetchall())[0]["CurrencyExchangeSnapshotId"]