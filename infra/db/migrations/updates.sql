ALTER TABLE game
ADD COLUMN ggg_api_trade_identifier VARCHAR(8);

UPDATE game
SET ggg_api_trade_identifier = 'trade2'
WHERE game_id = 2;

UPDATE game
SET ggg_api_trade_identifier = 'trade'
WHERE game_id = 1;

ALTER TABLE currency_exchange_snapshot
DROP CONSTRAINT IF EXISTS currency_exchange_snapshot_league_id_epoch_key;

ALTER TABLE currency_exchange_snapshot
DROP CONSTRAINT IF EXISTS currency_exchange_snapshot_league_id_realm_id_epoch_key;

ALTER TABLE currency_exchange_snapshot
ADD CONSTRAINT currency_exchange_snapshot_league_id_realm_id_epoch_key
UNIQUE (league_id, realm_id, epoch);
