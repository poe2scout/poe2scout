-- any table that has information on it needs a realm / game identifier.

--Tables that dont need either:
--item_category - Just stores api id and a label. Is automatically created. Not specific per realm.
--item_type - points towards an item_category. Duplicate item_categorys might exist but thats fine. Doesnt need a realm
--item - points to a base_item which has a game setting.
--unique-item - points to item which points to base_item which has a game setting
--currency_item - points to item which points to base_item which has a game setting
--currency_category. Similiar to item category. Just stores data.

--Tables that do need game:
--base_item - stores game specific images.
--league - leagues are according to game not realm.

--New tables:

--Realm(realm str, game str) EG poe2 / poe2 pc / poe xbox / poe sony / poe

--items will be per game.
--price_logs will be per league. If a league is "active" then we will fetch price_logs for that league in all realms of a game. this is simple for poe2 as of now cause there is only one realm. But in the future there will be 3 poe ones.
--realm identifier will need to be added to price_log table and currency exchange table.

--Possible issues: items change over time. We will ignore this. Currently if an item changes then a new item is made in our db. 
--This wont really be an issue cause we are only ever fetching the current league.


CREATE TABLE game (
    game_id SERIAL PRIMARY KEY,
    api_id character varying(300) NOT NULL,
    label character varying(300) NOT NULL
);

CREATE TABLE realm (
    realm_id SERIAL PRIMARY KEY,
	game_id integer NOT NULL REFERENCES game (game_id),
	api_id character varying(300) NOT NULL
);

INSERT INTO game(api_id, label)
VALUES ('poe', 'Path of Exile'), ('poe2', 'Path of Exile 2');

INSERT INTO realm(game_id, api_id)
VALUES (1, 'pc'), (1,'xbox'), (1,'sony'), (2, 'poe2')

ALTER TABLE league
ADD COLUMN game_id integer NOT NULL REFERENCES game (game_id) DEFAULT 2;

ALTER TABLE league
ADD COLUMN base_currency_item_id integer REFERENCES item (item_id);

ALTER TABLE base_item
ADD COLUMN game_id integer NOT NULL REFERENCES game (game_id) DEFAULT 2;

ALTER TABLE price_log
ADD COLUMN realm_id integer NOT NULL REFERENCES realm (realm_id) DEFAULT 4;

ALTER TABLE currency_exchange_snapshot
ADD COLUMN realm_id integer NOT NULL REFERENCES realm (realm_id) DEFAULT 4;

ALTER TABLE currency_exchange_history
ADD COLUMN realm_id integer NOT NULL REFERENCES realm (realm_id) DEFAULT 4;

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

CREATE OR REPLACE FUNCTION initialize_currency_history()
RETURNS void AS $$
BEGIN
    DROP TABLE IF EXISTS currency_exchange_history_build;

    CREATE UNLOGGED TABLE currency_exchange_history_build AS
    SELECT
        ces.epoch,
        ces.league_id,
        ces.realm_id,
        cesp.currency_exchange_snapshot_pair_id,
        cesp.currency_one_item_id,
        c1.value_traded AS c1_value_traded,
        c1.relative_price AS c1_relative_price,
        c1.stock_value AS c1_stock_value,
        c1.volume_traded AS c1_volume_traded,
        c1.highest_stock AS c1_highest_stock,
        cesp.currency_two_item_id,
        c2.value_traded AS c2_value_traded,
        c2.relative_price AS c2_relative_price,
        c2.stock_value AS c2_stock_value,
        c2.volume_traded AS c2_volume_traded,
        c2.highest_stock AS c2_highest_stock
    FROM currency_exchange_snapshot_pair AS cesp
    JOIN currency_exchange_snapshot AS ces
        ON ces.currency_exchange_snapshot_id = cesp.currency_exchange_snapshot_id
    JOIN LATERAL (
        SELECT
            cespd.value_traded,
            cespd.relative_price,
            cespd.stock_value,
            cespd.volume_traded,
            cespd.highest_stock
        FROM currency_exchange_snapshot_pair_data AS cespd
        WHERE cespd.currency_exchange_snapshot_pair_id = cesp.currency_exchange_snapshot_pair_id
          AND cespd.item_id = cesp.currency_one_item_id
    ) AS c1 ON TRUE
    JOIN LATERAL (
        SELECT
            cespd.value_traded,
            cespd.relative_price,
            cespd.stock_value,
            cespd.volume_traded,
            cespd.highest_stock
        FROM currency_exchange_snapshot_pair_data AS cespd
        WHERE cespd.currency_exchange_snapshot_pair_id = cesp.currency_exchange_snapshot_pair_id
          AND cespd.item_id = cesp.currency_two_item_id
    ) AS c2 ON TRUE;

    CREATE INDEX idx_currency_exchange_history_build_epoch
        ON currency_exchange_history_build (epoch DESC);
    CREATE INDEX idx_currency_exchange_history_build_snapshot_pair_id
        ON currency_exchange_history_build (currency_exchange_snapshot_pair_id);
    CREATE INDEX idx_currency_exchange_history_build_league_c1_c2
        ON currency_exchange_history_build (league_id, currency_one_item_id, currency_two_item_id);
    CREATE INDEX idx_currency_exchange_history_build_league_c1_c2_epoch
        ON currency_exchange_history_build (league_id, currency_one_item_id, currency_two_item_id, epoch DESC);

    ANALYZE currency_exchange_history_build;

    DROP TABLE currency_exchange_history;
    ALTER TABLE currency_exchange_history_build RENAME TO currency_exchange_history;

    ALTER INDEX idx_currency_exchange_history_build_epoch
        RENAME TO idx_currency_exchange_history_epoch;
    ALTER INDEX idx_currency_exchange_history_build_snapshot_pair_id
        RENAME TO idx_currency_exchange_history_snapshot_pair_id;
    ALTER INDEX idx_currency_exchange_history_build_league_c1_c2
        RENAME TO idx_currency_exchange_history_league_c1_c2;
    ALTER INDEX idx_currency_exchange_history_build_league_c1_c2_epoch
        RENAME TO idx_currency_exchange_history_league_c1_c2_epoch;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION update_currency_history_incrementally()
RETURNS void AS $$
DECLARE
    last_epoch integer;
BEGIN
    SELECT COALESCE(max(epoch), 0) INTO last_epoch FROM currency_exchange_history;

    INSERT INTO currency_exchange_history
    SELECT
        ces.epoch,
        ces.league_id,
        ces.realm_id,
        cesp.currency_exchange_snapshot_pair_id,
        cesp.currency_one_item_id,
        cespd1.value_traded AS c1_value_traded,
        cespd1.relative_price AS c1_relative_price,
        cespd1.stock_value AS c1_stock_value,
        cespd1.volume_traded AS c1_volume_traded,
        cespd1.highest_stock AS c1_highest_stock,
        cesp.currency_two_item_id,
        cespd2.value_traded AS c2_value_traded,
        cespd2.relative_price AS c2_relative_price,
        cespd2.stock_value AS c2_stock_value,
        cespd2.volume_traded AS c2_volume_traded,
        cespd2.highest_stock AS c2_highest_stock
    FROM currency_exchange_snapshot AS ces
    JOIN currency_exchange_snapshot_pair AS cesp
        ON cesp.currency_exchange_snapshot_id = ces.currency_exchange_snapshot_id
    JOIN currency_exchange_snapshot_pair_data AS cespd1
        ON cespd1.currency_exchange_snapshot_pair_id = cesp.currency_exchange_snapshot_pair_id
        AND cespd1.item_id = cesp.currency_one_item_id
    JOIN currency_exchange_snapshot_pair_data AS cespd2
        ON cespd2.currency_exchange_snapshot_pair_id = cesp.currency_exchange_snapshot_pair_id
        AND cespd2.item_id = cesp.currency_two_item_id
    WHERE ces.epoch > last_epoch;
END;
$$ LANGUAGE plpgsql;
