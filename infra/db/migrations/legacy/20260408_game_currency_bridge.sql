CREATE TABLE IF NOT EXISTS game_currency_bridge (
    game_currency_bridge_id SERIAL PRIMARY KEY,
    game_id integer NOT NULL REFERENCES game (game_id),
    currency_item_id integer NOT NULL REFERENCES currency_item (currency_item_id),
    bridge_rank integer NOT NULL,
    UNIQUE (game_id, currency_item_id),
    UNIQUE (game_id, bridge_rank)
);

INSERT INTO game_currency_bridge (game_id, currency_item_id, bridge_rank)
SELECT bi.game_id,
       ci.currency_item_id,
       CASE ci.api_id
           WHEN 'divine' THEN CASE WHEN bi.game_id = 1 THEN 1 ELSE 2 END
           WHEN 'chaos' THEN 1
       END AS bridge_rank
  FROM currency_item AS ci
  JOIN item AS i
    ON i.item_id = ci.item_id
  JOIN base_item AS bi
    ON bi.base_item_id = i.base_item_id
 WHERE (bi.game_id = 1 AND ci.api_id = 'divine')
    OR (bi.game_id = 2 AND ci.api_id IN ('chaos', 'divine'))
ON CONFLICT (game_id, currency_item_id) DO UPDATE
    SET bridge_rank = EXCLUDED.bridge_rank;
