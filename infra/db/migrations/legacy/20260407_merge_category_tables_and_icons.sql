ALTER TABLE item_category
ADD COLUMN IF NOT EXISTS category_kind VARCHAR(32);

UPDATE item_category
   SET category_kind = 'item'
 WHERE category_kind IS NULL;

ALTER TABLE item_category
ALTER COLUMN category_kind SET NOT NULL;

ALTER TABLE item_category
DROP CONSTRAINT IF EXISTS item_category_category_kind_check;

ALTER TABLE item_category
ADD CONSTRAINT item_category_category_kind_check
CHECK (category_kind IN ('item', 'currency'));

CREATE UNIQUE INDEX IF NOT EXISTS uq_item_category_kind_api_id
    ON item_category (category_kind, api_id);

CREATE TEMP TABLE currency_category_merge_map (
    currency_category_id INTEGER PRIMARY KEY,
    item_category_id INTEGER NOT NULL
) ON COMMIT DROP;

INSERT INTO item_category (api_id, label, category_kind)
SELECT cc.api_id, cc.label, 'currency'
  FROM currency_category AS cc;

INSERT INTO currency_category_merge_map (currency_category_id, item_category_id)
SELECT cc.currency_category_id, ic.item_category_id
  FROM currency_category AS cc
  JOIN item_category AS ic
    ON ic.api_id = cc.api_id
   AND ic.category_kind = 'currency';

ALTER TABLE currency_item
ADD COLUMN IF NOT EXISTS item_category_id INTEGER;

UPDATE currency_item AS ci
   SET item_category_id = mapping.item_category_id
  FROM currency_category_merge_map AS mapping
 WHERE mapping.currency_category_id = ci.currency_category_id;

ALTER TABLE currency_item
ALTER COLUMN item_category_id SET NOT NULL;

ALTER TABLE currency_item
ADD CONSTRAINT currency_item_item_category_id_fkey
FOREIGN KEY (item_category_id) REFERENCES item_category (item_category_id);

CREATE INDEX IF NOT EXISTS idx_currency_item_item_category_id
    ON currency_item (item_category_id);

CREATE TABLE IF NOT EXISTS game_item_category_icon (
    game_category_icon_id SERIAL PRIMARY KEY,
    game_id INTEGER NOT NULL REFERENCES game (game_id),
    item_category_id INTEGER NOT NULL REFERENCES item_category (item_category_id),
    icon_url VARCHAR(300) NOT NULL,
    UNIQUE (game_id, item_category_id)
);

INSERT INTO game_item_category_icon (game_id, item_category_id, icon_url)
SELECT DISTINCT ON (bi.game_id, it.item_category_id)
       bi.game_id,
       it.item_category_id,
       ui.icon_url
  FROM unique_item AS ui
  JOIN item AS i
    ON i.item_id = ui.item_id
  JOIN base_item AS bi
    ON bi.base_item_id = i.base_item_id
  JOIN item_type AS it
    ON it.item_type_id = bi.item_type_id
  JOIN item_category AS ic
    ON ic.item_category_id = it.item_category_id
 WHERE ic.category_kind = 'item'
   AND NULLIF(ui.icon_url, '') IS NOT NULL
 ORDER BY bi.game_id, it.item_category_id, ui.item_id ASC
ON CONFLICT (game_id, item_category_id) DO UPDATE
    SET icon_url = EXCLUDED.icon_url;

INSERT INTO game_item_category_icon (game_id, item_category_id, icon_url)
SELECT DISTINCT ON (bi.game_id, ci.item_category_id)
       bi.game_id,
       ci.item_category_id,
       COALESCE(NULLIF(ci.icon_url, ''), NULLIF(bi.icon_url, '')) AS icon_url
  FROM currency_item AS ci
  JOIN item AS i
    ON i.item_id = ci.item_id
  JOIN base_item AS bi
    ON bi.base_item_id = i.base_item_id
  JOIN item_category AS ic
    ON ic.item_category_id = ci.item_category_id
 WHERE ic.category_kind = 'currency'
   AND COALESCE(NULLIF(ci.icon_url, ''), NULLIF(bi.icon_url, '')) IS NOT NULL
 ORDER BY bi.game_id, ci.item_category_id, ci.item_id ASC
ON CONFLICT (game_id, item_category_id) DO UPDATE
    SET icon_url = EXCLUDED.icon_url;

ALTER TABLE currency_item
DROP CONSTRAINT IF EXISTS currency_item_currency_category_id_fkey;

ALTER TABLE currency_item
DROP COLUMN currency_category_id;

DROP TABLE currency_category;
