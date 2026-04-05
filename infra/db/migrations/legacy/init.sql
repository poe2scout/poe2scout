DROP SCHEMA public CASCADE;
CREATE SCHEMA public;

GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;

CREATE TABLE item_category (
    item_category_id SERIAL PRIMARY KEY,
    api_id character varying(300) NOT NULL,
    label character varying(300) NOT NULL
);

CREATE TABLE item_type (
    item_type_id SERIAL PRIMARY KEY,
    value character varying(300) NOT NULL,
    item_category_id integer NOT NULL REFERENCES item_category (item_category_id)
);

CREATE TABLE base_item (
    base_item_id SERIAL PRIMARY KEY,
    item_type_id integer NOT NULL REFERENCES item_type (item_type_id),
    icon_url character varying(300),
    item_metadata json
);

CREATE TABLE item (
    item_id SERIAL PRIMARY KEY,
    base_item_id integer NOT NULL REFERENCES base_item (base_item_id),
    item_type character varying(50) NOT NULL
);

CREATE TABLE unique_item (
    unique_item_id SERIAL PRIMARY KEY,
    item_id integer NOT NULL REFERENCES item (item_id),
    icon_url character varying(300),
    name character varying(300),
    text character varying(300),
    item_metadata json,
    is_chanceable boolean NOT NULL DEFAULT FALSE
);

CREATE TABLE currency_category (
    currency_category_id SERIAL PRIMARY KEY,
    api_id character varying(300) NOT NULL,
    label character varying(300) NOT NULL
);

CREATE TABLE currency_item (
    currency_item_id SERIAL PRIMARY KEY,
    item_id integer NOT NULL REFERENCES item (item_id),
    currency_category_id integer NOT NULL REFERENCES currency_category (currency_category_id),
    api_id character varying(300) NOT NULL,
    text character varying(300) NOT NULL,
    icon_url character varying(300),
    item_metadata json
);

CREATE TABLE league (
    league_id SERIAL PRIMARY KEY,
    value character varying(300) NOT NULL,
    current_league boolean NOT NULL DEFAULT TRUE
);

CREATE TABLE price_log (
    price_log_id SERIAL PRIMARY KEY,
    item_id integer NOT NULL REFERENCES item (item_id),
    price double precision NOT NULL,
    created_at timestamp without time zone NOT NULL,
    quantity integer NOT NULL,
    league_id integer NOT NULL REFERENCES league (league_id)
);

CREATE TABLE currency_exchange_snapshot (
    currency_exchange_snapshot_id SERIAL PRIMARY KEY,
    epoch integer NOT NULL,
    league_id integer NOT NULL REFERENCES league (league_id),
    volume decimal(20, 8),
    market_cap decimal(20, 8)
);

CREATE SEQUENCE currency_exchange_snapshot_pair_id_seq;

CREATE TABLE currency_exchange_snapshot_pair (
    currency_exchange_snapshot_pair_id integer NOT NULL
        DEFAULT nextval('currency_exchange_snapshot_pair_id_seq') PRIMARY KEY,
    currency_exchange_snapshot_id integer NOT NULL REFERENCES currency_exchange_snapshot (currency_exchange_snapshot_id),
    currency_one_item_id integer NOT NULL REFERENCES item (item_id),
    currency_two_item_id integer NOT NULL REFERENCES item (item_id),
    volume decimal(20, 8) NOT NULL
);

ALTER SEQUENCE currency_exchange_snapshot_pair_id_seq
    OWNED BY currency_exchange_snapshot_pair.currency_exchange_snapshot_pair_id;

CREATE TABLE currency_exchange_snapshot_pair_data (
    currency_exchange_snapshot_pair_id integer NOT NULL,
    item_id integer NOT NULL,
    value_traded decimal(20, 8) NOT NULL,
    relative_price decimal(20, 8) NOT NULL,
    stock_value decimal(20, 8) NOT NULL,
    volume_traded bigint NOT NULL,
    highest_stock bigint NOT NULL,
    PRIMARY KEY (currency_exchange_snapshot_pair_id, item_id)
);

CREATE TABLE service_cache (
    service_cache_id SERIAL PRIMARY KEY,
    service_name varchar(100) NOT NULL,
    value integer NOT NULL
);

CREATE UNLOGGED TABLE currency_exchange_history (
    epoch integer NOT NULL,
    league_id integer,
    currency_exchange_snapshot_pair_id integer NOT NULL,
    currency_one_item_id integer,
    c1_value_traded decimal(20, 8),
    c1_relative_price decimal(20, 8),
    c1_stock_value decimal(20, 8),
    c1_volume_traded bigint,
    c1_highest_stock bigint,
    currency_two_item_id integer,
    c2_value_traded decimal(20, 8),
    c2_relative_price decimal(20, 8),
    c2_stock_value decimal(20, 8),
    c2_volume_traded bigint,
    c2_highest_stock bigint
);

CREATE INDEX idx_base_item_item_type_id ON base_item (item_type_id);
CREATE INDEX idx_item_base_item_id ON item (base_item_id);
CREATE INDEX idx_item_item_type ON item (item_type);
CREATE INDEX idx_price_log_league_id ON price_log (league_id);
CREATE INDEX idx_price_log_item_league_created_at ON price_log (item_id, league_id, created_at DESC);
CREATE INDEX idx_price_log_league_item_created_at_covering
    ON price_log (league_id, item_id, created_at DESC, price, quantity);

CREATE INDEX idx_currency_exchange_history_epoch ON currency_exchange_history (epoch DESC);
CREATE INDEX idx_currency_exchange_history_snapshot_pair_id
    ON currency_exchange_history (currency_exchange_snapshot_pair_id);
CREATE INDEX idx_currency_exchange_history_league_c1_c2
    ON currency_exchange_history (league_id, currency_one_item_id, currency_two_item_id);
CREATE INDEX idx_currency_exchange_history_league_c1_c2_epoch
    ON currency_exchange_history (league_id, currency_one_item_id, currency_two_item_id, epoch DESC);

CREATE OR REPLACE FUNCTION initialize_currency_history()
RETURNS void AS $$
BEGIN
    DROP TABLE IF EXISTS currency_exchange_history_build;

    CREATE UNLOGGED TABLE currency_exchange_history_build AS
    SELECT
        ces.epoch,
        ces.league_id,
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
