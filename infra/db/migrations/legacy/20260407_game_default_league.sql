ALTER TABLE game
ADD COLUMN IF NOT EXISTS default_league_id integer;

ALTER TABLE game
ADD CONSTRAINT game_default_league_id_fkey
FOREIGN KEY (default_league_id) REFERENCES league (league_id);

UPDATE game
   SET default_league_id = 21
 WHERE game_id = 1;

UPDATE game
   SET default_league_id = 7
 WHERE game_id = 2;

ALTER TABLE game
ALTER COLUMN default_league_id SET NOT NULL;
