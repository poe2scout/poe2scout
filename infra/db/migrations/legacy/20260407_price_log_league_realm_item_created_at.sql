CREATE INDEX IF NOT EXISTS idx_price_log_league_realm_item_created_at_covering
    ON price_log (league_id, realm_id, item_id, created_at DESC)
    INCLUDE (price, quantity);
