ALTER TABLE league
ADD COLUMN IF NOT EXISTS base_currency_item_id integer REFERENCES item (item_id);

CREATE OR REPLACE FUNCTION get_default_league_base_currency_item_id(target_game_id integer)
RETURNS integer AS $$
DECLARE
    desired_api_id varchar(32);
    selected_item_id integer;
BEGIN
    desired_api_id := CASE WHEN target_game_id = 1 THEN 'chaos' ELSE 'exalted' END;

    SELECT ci.item_id
      INTO selected_item_id
      FROM currency_item AS ci
      JOIN item AS i ON i.item_id = ci.item_id
      JOIN base_item AS bi ON bi.base_item_id = i.base_item_id
     WHERE ci.api_id = desired_api_id
       AND bi.game_id = target_game_id
     LIMIT 1;

    RETURN selected_item_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION set_league_base_currency_item_id()
RETURNS trigger AS $$
BEGIN
    IF NEW.base_currency_item_id IS NULL THEN
        NEW.base_currency_item_id := get_default_league_base_currency_item_id(NEW.game_id);
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS league_set_base_currency_item_id ON league;

CREATE TRIGGER league_set_base_currency_item_id
BEFORE INSERT OR UPDATE OF game_id, base_currency_item_id
ON league
FOR EACH ROW
EXECUTE FUNCTION set_league_base_currency_item_id();

UPDATE league
   SET base_currency_item_id = get_default_league_base_currency_item_id(game_id)
 WHERE base_currency_item_id IS NULL;
