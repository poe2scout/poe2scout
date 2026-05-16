ALTER TABLE league
ADD COLUMN IF NOT EXISTS short_name character varying(80);

ALTER TABLE league
ADD CONSTRAINT league_short_name_not_blank
CHECK (short_name IS NULL OR btrim(short_name) <> '');

CREATE UNIQUE INDEX IF NOT EXISTS league_game_short_name_unique_idx
ON league (game_id, lower(short_name))
WHERE short_name IS NOT NULL;

-- Fill short_name values before applying the NOT NULL constraint.
-- Example:
-- UPDATE league
-- SET short_name = 'fate'
-- WHERE value = 'Fate of the Vaal';

-- Check for any remaining missing values:
-- SELECT league_id, game_id, value
-- FROM league
-- WHERE short_name IS NULL
-- ORDER BY game_id, value;

-- Optional collision check because API lookups accept both value and short_name:
-- SELECT a.league_id AS short_name_league_id,
--        a.value AS short_name_league,
--        a.short_name,
--        b.league_id AS value_league_id,
--        b.value AS colliding_value
-- FROM league a
-- JOIN league b
--   ON a.game_id = b.game_id
--  AND lower(a.short_name) = lower(b.value)
--  AND a.league_id <> b.league_id;

ALTER TABLE league
ALTER COLUMN short_name SET NOT NULL;
