ALTER TABLE item_daily_stats
ADD COLUMN IF NOT EXISTS volume integer;

WITH daily_volume AS (
    SELECT
        realm_id,
        item_id,
        league_id,
        created_at::date AS day,
        sum(quantity)::int AS volume
      FROM price_log
     GROUP BY realm_id, item_id, league_id, created_at::date
)
UPDATE item_daily_stats AS ids
   SET volume = daily_volume.volume
  FROM daily_volume
 WHERE ids.realm_id = daily_volume.realm_id
   AND ids.item_id = daily_volume.item_id
   AND ids.league_id = daily_volume.league_id
   AND ids.day = daily_volume.day;

UPDATE item_daily_stats
   SET volume = 0
 WHERE volume IS NULL;

ALTER TABLE item_daily_stats
ALTER COLUMN volume SET NOT NULL;
