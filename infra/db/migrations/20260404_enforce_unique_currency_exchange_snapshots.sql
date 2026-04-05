BEGIN;

CREATE TEMP TABLE snapshots_to_delete ON COMMIT DROP AS
WITH duplicate_snapshots AS (
    SELECT
        currency_exchange_snapshot_id,
        ROW_NUMBER() OVER (
            PARTITION BY league_id, epoch
            ORDER BY random()
        ) AS duplicate_rank
    FROM currency_exchange_snapshot
)
SELECT currency_exchange_snapshot_id
FROM duplicate_snapshots
WHERE duplicate_rank > 1;

CREATE TEMP TABLE pairs_to_delete ON COMMIT DROP AS
SELECT currency_exchange_snapshot_pair_id
FROM currency_exchange_snapshot_pair
WHERE currency_exchange_snapshot_id IN (
    SELECT currency_exchange_snapshot_id
    FROM snapshots_to_delete
);

DELETE FROM currency_exchange_snapshot_pair_data
WHERE currency_exchange_snapshot_pair_id IN (
    SELECT currency_exchange_snapshot_pair_id
    FROM pairs_to_delete
);

DELETE FROM currency_exchange_snapshot_pair
WHERE currency_exchange_snapshot_id IN (
    SELECT currency_exchange_snapshot_id
    FROM snapshots_to_delete
);

DELETE FROM currency_exchange_snapshot
WHERE currency_exchange_snapshot_id IN (
    SELECT currency_exchange_snapshot_id
    FROM snapshots_to_delete
);

SELECT initialize_currency_history();

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'currency_exchange_snapshot_league_id_epoch_key'
    ) THEN
        ALTER TABLE currency_exchange_snapshot
            ADD CONSTRAINT currency_exchange_snapshot_league_id_epoch_key
            UNIQUE (league_id, epoch);
    END IF;
END;
$$;

COMMIT;
