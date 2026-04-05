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

ALTER TABLE base_item
ADD COLUMN game_id integer NOT NULL REFERENCES game (game_id) DEFAULT 2;

ALTER TABLE price_log
ADD COLUMN realm_id integer NOT NULL REFERENCES realm (realm_id) DEFAULT 4;

ALTER TABLE currency_exchange_snapshot
ADD COLUMN realm_id integer NOT NULL REFERENCES realm (realm_id) DEFAULT 4;
