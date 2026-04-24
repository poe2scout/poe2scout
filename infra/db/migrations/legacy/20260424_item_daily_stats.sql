-- Creates and backfills daily item price aggregates.
--
-- Production may not exactly match a local development schema, so fail early if the
-- source table does not expose the columns needed by the backfill and write path.
DO $$
BEGIN
    IF EXISTS (
        SELECT required.column_name
          FROM (
              VALUES
                  ('item_id'),
                  ('league_id'),
                  ('realm_id'),
                  ('price'),
                  ('created_at')
          ) AS required(column_name)
         WHERE NOT EXISTS (
             SELECT 1
               FROM information_schema.columns AS columns
              WHERE columns.table_schema = 'public'
                AND columns.table_name = 'price_log'
                AND columns.column_name = required.column_name
         )
    ) THEN
        RAISE EXCEPTION 'price_log is missing one or more columns required for item_daily_stats';
    END IF;
END $$;

CREATE TABLE IF NOT EXISTS item_daily_stats (
    item_daily_stats_id SERIAL PRIMARY KEY,
    realm_id integer NOT NULL REFERENCES realm (realm_id),
    item_id integer NOT NULL REFERENCES item (item_id),
    league_id integer NOT NULL REFERENCES league (league_id),
    day date NOT NULL,
    open_price double precision NOT NULL,
    close_price double precision NOT NULL,
    min_price double precision NOT NULL,
    max_price double precision NOT NULL,
    avg_price double precision NOT NULL,
    data_points integer NOT NULL,
    CONSTRAINT item_daily_stats_realm_item_league_day_key
        UNIQUE (realm_id, item_id, league_id, day)
);

CREATE INDEX IF NOT EXISTS idx_item_daily_stats_league_realm_item_day
    ON item_daily_stats (league_id, realm_id, item_id, day DESC);

-- Idempotent backfill. Run off-hours; for chunked runs, add a created_at date range
-- predicate to source_price_logs and rerun each chunk.
WITH source_price_logs AS (
    SELECT
        price_log_id,
        realm_id,
        item_id,
        league_id,
        price,
        created_at
      FROM price_log
),
ranked_price_logs AS (
    SELECT
        realm_id,
        item_id,
        league_id,
        created_at::date AS day,
        price,
        row_number() OVER (
            PARTITION BY realm_id, item_id, league_id, created_at::date
            ORDER BY created_at ASC, price_log_id ASC
        ) AS open_rank,
        row_number() OVER (
            PARTITION BY realm_id, item_id, league_id, created_at::date
            ORDER BY created_at DESC, price_log_id DESC
        ) AS close_rank
      FROM source_price_logs
),
daily_stats AS (
    SELECT
        realm_id,
        item_id,
        league_id,
        day,
        max(price) FILTER (WHERE open_rank = 1) AS open_price,
        max(price) FILTER (WHERE close_rank = 1) AS close_price,
        min(price) AS min_price,
        max(price) AS max_price,
        avg(price) AS avg_price,
        count(*)::int AS data_points
      FROM ranked_price_logs
     GROUP BY realm_id, item_id, league_id, day
)
INSERT INTO item_daily_stats (
    realm_id,
    item_id,
    league_id,
    day,
    open_price,
    close_price,
    min_price,
    max_price,
    avg_price,
    data_points
)
SELECT
    realm_id,
    item_id,
    league_id,
    day,
    open_price,
    close_price,
    min_price,
    max_price,
    avg_price,
    data_points
  FROM daily_stats
ON CONFLICT (realm_id, item_id, league_id, day) DO UPDATE SET
    open_price = EXCLUDED.open_price,
    close_price = EXCLUDED.close_price,
    min_price = EXCLUDED.min_price,
    max_price = EXCLUDED.max_price,
    avg_price = EXCLUDED.avg_price,
    data_points = EXCLUDED.data_points;
