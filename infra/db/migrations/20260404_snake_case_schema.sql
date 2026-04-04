BEGIN;

DROP FUNCTION IF EXISTS initialize_currency_history();
DROP FUNCTION IF EXISTS update_currency_history_incrementally();

ALTER TABLE IF EXISTS "ItemCategory" RENAME TO item_category;
ALTER TABLE IF EXISTS "ItemType" RENAME TO item_type;
ALTER TABLE IF EXISTS "BaseItem" RENAME TO base_item;
ALTER TABLE IF EXISTS "Item" RENAME TO item;
ALTER TABLE IF EXISTS "UniqueItem" RENAME TO unique_item;
ALTER TABLE IF EXISTS "CurrencyCategory" RENAME TO currency_category;
ALTER TABLE IF EXISTS "CurrencyItem" RENAME TO currency_item;
ALTER TABLE IF EXISTS "League" RENAME TO league;
ALTER TABLE IF EXISTS "PriceLog" RENAME TO price_log;
ALTER TABLE IF EXISTS "CurrencyExchangeSnapshot" RENAME TO currency_exchange_snapshot;
ALTER TABLE IF EXISTS "CurrencyExchangeSnapshotPair" RENAME TO currency_exchange_snapshot_pair;
ALTER TABLE IF EXISTS "CurrencyExchangeSnapshotPairData" RENAME TO currency_exchange_snapshot_pair_data;
ALTER TABLE IF EXISTS "ServiceCache" RENAME TO service_cache;

ALTER TABLE item_category RENAME COLUMN "id" TO item_category_id;
ALTER TABLE item_category RENAME COLUMN "apiId" TO api_id;

ALTER TABLE item_type RENAME COLUMN "id" TO item_type_id;
ALTER TABLE item_type RENAME COLUMN "categoryId" TO item_category_id;

ALTER TABLE base_item RENAME COLUMN "id" TO base_item_id;
ALTER TABLE base_item RENAME COLUMN "typeId" TO item_type_id;
ALTER TABLE base_item RENAME COLUMN "iconUrl" TO icon_url;
ALTER TABLE base_item RENAME COLUMN "itemMetadata" TO item_metadata;

ALTER TABLE item RENAME COLUMN "id" TO item_id;
ALTER TABLE item RENAME COLUMN "baseItemId" TO base_item_id;
ALTER TABLE item RENAME COLUMN "itemType" TO item_type;

ALTER TABLE unique_item RENAME COLUMN "id" TO unique_item_id;
ALTER TABLE unique_item RENAME COLUMN "itemId" TO item_id;
ALTER TABLE unique_item RENAME COLUMN "iconUrl" TO icon_url;
ALTER TABLE unique_item RENAME COLUMN "itemMetadata" TO item_metadata;

ALTER TABLE currency_category RENAME COLUMN "id" TO currency_category_id;
ALTER TABLE currency_category RENAME COLUMN "apiId" TO api_id;

ALTER TABLE currency_item RENAME COLUMN "id" TO currency_item_id;
ALTER TABLE currency_item RENAME COLUMN "itemId" TO item_id;
ALTER TABLE currency_item RENAME COLUMN "currencyCategoryId" TO currency_category_id;
ALTER TABLE currency_item RENAME COLUMN "apiId" TO api_id;
ALTER TABLE currency_item RENAME COLUMN "iconUrl" TO icon_url;
ALTER TABLE currency_item RENAME COLUMN "itemMetadata" TO item_metadata;

ALTER TABLE league RENAME COLUMN "id" TO league_id;

ALTER TABLE price_log RENAME COLUMN "id" TO price_log_id;
ALTER TABLE price_log RENAME COLUMN "itemId" TO item_id;
ALTER TABLE price_log RENAME COLUMN "createdAt" TO created_at;
ALTER TABLE price_log RENAME COLUMN "leagueId" TO league_id;

ALTER TABLE currency_exchange_snapshot RENAME COLUMN "CurrencyExchangeSnapshotId" TO currency_exchange_snapshot_id;
ALTER TABLE currency_exchange_snapshot RENAME COLUMN "Epoch" TO epoch;
ALTER TABLE currency_exchange_snapshot RENAME COLUMN "LeagueId" TO league_id;
ALTER TABLE currency_exchange_snapshot RENAME COLUMN "Volume" TO volume;
ALTER TABLE currency_exchange_snapshot RENAME COLUMN "MarketCap" TO market_cap;

ALTER TABLE currency_exchange_snapshot_pair
    RENAME COLUMN "CurrencyExchangeSnapshotPairId" TO currency_exchange_snapshot_pair_id;
ALTER TABLE currency_exchange_snapshot_pair
    RENAME COLUMN "CurrencyExchangeSnapshotId" TO currency_exchange_snapshot_id;
ALTER TABLE currency_exchange_snapshot_pair RENAME COLUMN "CurrencyOneId" TO currency_one_item_id;
ALTER TABLE currency_exchange_snapshot_pair RENAME COLUMN "CurrencyTwoId" TO currency_two_item_id;
ALTER TABLE currency_exchange_snapshot_pair RENAME COLUMN "Volume" TO volume;

ALTER TABLE currency_exchange_snapshot_pair_data
    RENAME COLUMN "CurrencyExchangeSnapshotPairId" TO currency_exchange_snapshot_pair_id;
ALTER TABLE currency_exchange_snapshot_pair_data RENAME COLUMN "CurrencyId" TO item_id;
ALTER TABLE currency_exchange_snapshot_pair_data RENAME COLUMN "ValueTraded" TO value_traded;
ALTER TABLE currency_exchange_snapshot_pair_data RENAME COLUMN "RelativePrice" TO relative_price;
ALTER TABLE currency_exchange_snapshot_pair_data RENAME COLUMN "StockValue" TO stock_value;
ALTER TABLE currency_exchange_snapshot_pair_data RENAME COLUMN "VolumeTraded" TO volume_traded;
ALTER TABLE currency_exchange_snapshot_pair_data RENAME COLUMN "HighestStock" TO highest_stock;

ALTER TABLE service_cache RENAME COLUMN "ServiceCacheId" TO service_cache_id;
ALTER TABLE service_cache RENAME COLUMN "ServiceName" TO service_name;
ALTER TABLE service_cache RENAME COLUMN "Value" TO value;

ALTER TABLE currency_exchange_history RENAME COLUMN "Epoch" TO epoch;
ALTER TABLE currency_exchange_history RENAME COLUMN "LeagueId" TO league_id;
ALTER TABLE currency_exchange_history
    RENAME COLUMN "CurrencyExchangeSnapshotPairId" TO currency_exchange_snapshot_pair_id;
ALTER TABLE currency_exchange_history RENAME COLUMN "CurrencyOneId" TO currency_one_item_id;
ALTER TABLE currency_exchange_history RENAME COLUMN "C1_ValueTraded" TO c1_value_traded;
ALTER TABLE currency_exchange_history RENAME COLUMN "C1_RelativePrice" TO c1_relative_price;
ALTER TABLE currency_exchange_history RENAME COLUMN "C1_StockValue" TO c1_stock_value;
ALTER TABLE currency_exchange_history RENAME COLUMN "C1_VolumeTraded" TO c1_volume_traded;
ALTER TABLE currency_exchange_history RENAME COLUMN "C1_HighestStock" TO c1_highest_stock;
ALTER TABLE currency_exchange_history RENAME COLUMN "CurrencyTwoId" TO currency_two_item_id;
ALTER TABLE currency_exchange_history RENAME COLUMN "C2_ValueTraded" TO c2_value_traded;
ALTER TABLE currency_exchange_history RENAME COLUMN "C2_RelativePrice" TO c2_relative_price;
ALTER TABLE currency_exchange_history RENAME COLUMN "C2_StockValue" TO c2_stock_value;
ALTER TABLE currency_exchange_history RENAME COLUMN "C2_VolumeTraded" TO c2_volume_traded;
ALTER TABLE currency_exchange_history RENAME COLUMN "C2_HighestStock" TO c2_highest_stock;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'unique_item'
          AND column_name = 'isChanceable'
    ) THEN
        ALTER TABLE unique_item RENAME COLUMN "isChanceable" TO is_chanceable;
    END IF;
END;
$$;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'league'
          AND column_name = 'currentLeague'
    ) THEN
        ALTER TABLE league RENAME COLUMN "currentLeague" TO current_league;
    END IF;
END;
$$;

ALTER SEQUENCE IF EXISTS "ItemCategory_id_seq" RENAME TO item_category_item_category_id_seq;
ALTER SEQUENCE IF EXISTS "ItemType_id_seq" RENAME TO item_type_item_type_id_seq;
ALTER SEQUENCE IF EXISTS "BaseItem_id_seq" RENAME TO base_item_base_item_id_seq;
ALTER SEQUENCE IF EXISTS "Item_id_seq" RENAME TO item_item_id_seq;
ALTER SEQUENCE IF EXISTS "UniqueItem_id_seq" RENAME TO unique_item_unique_item_id_seq;
ALTER SEQUENCE IF EXISTS "CurrencyCategory_id_seq" RENAME TO currency_category_currency_category_id_seq;
ALTER SEQUENCE IF EXISTS "CurrencyItem_id_seq" RENAME TO currency_item_currency_item_id_seq;
ALTER SEQUENCE IF EXISTS "League_id_seq" RENAME TO league_league_id_seq;
ALTER SEQUENCE IF EXISTS "PriceLog_id_seq" RENAME TO price_log_price_log_id_seq;
ALTER SEQUENCE IF EXISTS "CurrencyExchangeSnapshot_CurrencyExchangeSnapshotId_seq"
    RENAME TO currency_exchange_snapshot_currency_exchange_snapshot_id_seq;
ALTER SEQUENCE IF EXISTS "ServiceCache_ServiceCacheId_seq"
    RENAME TO service_cache_service_cache_id_seq;

DO $$
DECLARE
    owned_sequence_name text;
BEGIN
    SELECT sequence_name
    INTO owned_sequence_name
    FROM information_schema.sequences
    WHERE sequence_schema = 'public'
      AND sequence_name = 'currency_exchange_snapshot_pair_id_seq';

    IF owned_sequence_name IS NULL THEN
        SELECT sequence.relname
        INTO owned_sequence_name
        FROM pg_class AS sequence
        JOIN pg_depend AS dependency ON dependency.objid = sequence.oid
        JOIN pg_class AS table_ref ON table_ref.oid = dependency.refobjid
        JOIN pg_attribute AS column_ref
            ON column_ref.attrelid = table_ref.oid
            AND column_ref.attnum = dependency.refobjsubid
        WHERE sequence.relkind = 'S'
          AND dependency.deptype = 'a'
          AND table_ref.relname = 'currency_exchange_snapshot_pair'
          AND column_ref.attname = 'currency_exchange_snapshot_pair_id';

        IF owned_sequence_name IS NOT NULL THEN
            EXECUTE format(
                'ALTER SEQUENCE %I RENAME TO currency_exchange_snapshot_pair_id_seq',
                owned_sequence_name
            );
        ELSE
            EXECUTE 'CREATE SEQUENCE currency_exchange_snapshot_pair_id_seq';
        END IF;
    END IF;
END;
$$;

ALTER TABLE item_category ALTER COLUMN item_category_id
    SET DEFAULT nextval('item_category_item_category_id_seq');
ALTER SEQUENCE item_category_item_category_id_seq OWNED BY item_category.item_category_id;

ALTER TABLE item_type ALTER COLUMN item_type_id
    SET DEFAULT nextval('item_type_item_type_id_seq');
ALTER SEQUENCE item_type_item_type_id_seq OWNED BY item_type.item_type_id;

ALTER TABLE base_item ALTER COLUMN base_item_id
    SET DEFAULT nextval('base_item_base_item_id_seq');
ALTER SEQUENCE base_item_base_item_id_seq OWNED BY base_item.base_item_id;

ALTER TABLE item ALTER COLUMN item_id
    SET DEFAULT nextval('item_item_id_seq');
ALTER SEQUENCE item_item_id_seq OWNED BY item.item_id;

ALTER TABLE unique_item ALTER COLUMN unique_item_id
    SET DEFAULT nextval('unique_item_unique_item_id_seq');
ALTER SEQUENCE unique_item_unique_item_id_seq OWNED BY unique_item.unique_item_id;

ALTER TABLE currency_category ALTER COLUMN currency_category_id
    SET DEFAULT nextval('currency_category_currency_category_id_seq');
ALTER SEQUENCE currency_category_currency_category_id_seq OWNED BY currency_category.currency_category_id;

ALTER TABLE currency_item ALTER COLUMN currency_item_id
    SET DEFAULT nextval('currency_item_currency_item_id_seq');
ALTER SEQUENCE currency_item_currency_item_id_seq OWNED BY currency_item.currency_item_id;

ALTER TABLE league ALTER COLUMN league_id
    SET DEFAULT nextval('league_league_id_seq');
ALTER SEQUENCE league_league_id_seq OWNED BY league.league_id;

ALTER TABLE price_log ALTER COLUMN price_log_id
    SET DEFAULT nextval('price_log_price_log_id_seq');
ALTER SEQUENCE price_log_price_log_id_seq OWNED BY price_log.price_log_id;

ALTER TABLE currency_exchange_snapshot ALTER COLUMN currency_exchange_snapshot_id
    SET DEFAULT nextval('currency_exchange_snapshot_currency_exchange_snapshot_id_seq');
ALTER SEQUENCE currency_exchange_snapshot_currency_exchange_snapshot_id_seq
    OWNED BY currency_exchange_snapshot.currency_exchange_snapshot_id;

ALTER TABLE currency_exchange_snapshot_pair ALTER COLUMN currency_exchange_snapshot_pair_id
    SET DEFAULT nextval('currency_exchange_snapshot_pair_id_seq');
ALTER SEQUENCE currency_exchange_snapshot_pair_id_seq
    OWNED BY currency_exchange_snapshot_pair.currency_exchange_snapshot_pair_id;

ALTER TABLE service_cache ALTER COLUMN service_cache_id
    SET DEFAULT nextval('service_cache_service_cache_id_seq');
ALTER SEQUENCE service_cache_service_cache_id_seq OWNED BY service_cache.service_cache_id;

DO $$
DECLARE
    index_record record;
BEGIN
    FOR index_record IN
        SELECT indexname
        FROM pg_indexes
        WHERE schemaname = 'public'
          AND tablename = 'price_log'
          AND indexname <> 'PriceLog_pkey'
    LOOP
        EXECUTE format('DROP INDEX IF EXISTS %I', index_record.indexname);
    END LOOP;
END;
$$;

DO $$
DECLARE
    index_record record;
BEGIN
    FOR index_record IN
        SELECT indexname
        FROM pg_indexes
        WHERE schemaname = 'public'
          AND tablename = 'currency_exchange_history'
    LOOP
        EXECUTE format('DROP INDEX IF EXISTS %I', index_record.indexname);
    END LOOP;
END;
$$;

ALTER INDEX IF EXISTS "idx_baseitem_typeId" RENAME TO idx_base_item_item_type_id;
ALTER INDEX IF EXISTS "idx_item_baseItemId" RENAME TO idx_item_base_item_id;
ALTER INDEX IF EXISTS "idx_item_itemType" RENAME TO idx_item_item_type;

CREATE INDEX IF NOT EXISTS idx_price_log_league_id ON price_log (league_id);
CREATE INDEX IF NOT EXISTS idx_price_log_item_league_created_at
    ON price_log (item_id, league_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_price_log_league_item_created_at_covering
    ON price_log (league_id, item_id, created_at DESC, price, quantity);

CREATE INDEX IF NOT EXISTS idx_currency_exchange_history_epoch
    ON currency_exchange_history (epoch DESC);
CREATE INDEX IF NOT EXISTS idx_currency_exchange_history_snapshot_pair_id
    ON currency_exchange_history (currency_exchange_snapshot_pair_id);
CREATE INDEX IF NOT EXISTS idx_currency_exchange_history_league_c1_c2
    ON currency_exchange_history (league_id, currency_one_item_id, currency_two_item_id);
CREATE INDEX IF NOT EXISTS idx_currency_exchange_history_league_c1_c2_epoch
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

COMMIT;
