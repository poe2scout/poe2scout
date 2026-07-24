\set ON_ERROR_STOP on

DO $$
DECLARE
    conflict_count integer;
    sample_game_id integer;
    sample_api_id text;
    sample_base_item_type_id text;
    api_item_id integer;
    base_item_id integer;
BEGIN
    SELECT COUNT(*)
    INTO conflict_count
    FROM (
        SELECT bi.game_id, ci.base_item_type_id
        FROM currency_item ci
        JOIN item i USING (item_id)
        JOIN base_item bi USING (base_item_id)
        WHERE ci.base_item_type_id IS NOT NULL
        GROUP BY bi.game_id, ci.base_item_type_id
        HAVING COUNT(*) > 1
    ) duplicate_base_ids;

    IF conflict_count <> 0 THEN
        RAISE EXCEPTION '% duplicate per-game base item type IDs remain', conflict_count;
    END IF;

    SELECT COUNT(*)
    INTO conflict_count
    FROM currency_item
    WHERE api_id IN (
        'abyss-key',
        'essence-of-abyss',
        'omen-of-abyssal-favours',
        'rite-of-passage',
        'serpent-idol',
        'blessing-general'
    );

    IF conflict_count <> 0 THEN
        RAISE EXCEPTION '% retired currency aliases still resolve', conflict_count;
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM currency_item
        WHERE api_id = 'loyalty-tattoo-of-ikiaho'
          AND base_item_type_id IS NOT NULL
    ) OR NOT EXISTS (
        SELECT 1
        FROM currency_item
        WHERE api_id = 'loyalty-tattoo-of-ikiahoCopy'
          AND base_item_type_id IS NULL
    ) THEN
        RAISE EXCEPTION 'Loyalty Tattoo canonical/Copy mapping invariant failed';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM league l
        JOIN currency_item ci ON ci.item_id = l.base_currency_item_id
        WHERE ci.base_item_type_id IS NULL
    ) THEN
        RAISE EXCEPTION 'A league base currency is missing a base item type ID';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM game_currency_bridge bridge
        JOIN currency_item ci USING (currency_item_id)
        WHERE ci.base_item_type_id IS NULL
    ) THEN
        RAISE EXCEPTION 'A bridge currency is missing a base item type ID';
    END IF;

    SELECT bi.game_id, ci.api_id, ci.base_item_type_id
    INTO STRICT sample_game_id, sample_api_id, sample_base_item_type_id
    FROM currency_item ci
    JOIN item i USING (item_id)
    JOIN base_item bi USING (base_item_id)
    WHERE ci.api_id IS NOT NULL
      AND ci.base_item_type_id IS NOT NULL
    ORDER BY ci.currency_item_id
    LIMIT 1;

    SELECT ci.item_id
    INTO STRICT api_item_id
    FROM currency_item ci
    JOIN item i USING (item_id)
    JOIN base_item bi USING (base_item_id)
    WHERE bi.game_id = sample_game_id
      AND (ci.api_id = sample_api_id OR ci.base_item_type_id = sample_api_id);

    SELECT ci.item_id
    INTO STRICT base_item_id
    FROM currency_item ci
    JOIN item i USING (item_id)
    JOIN base_item bi USING (base_item_id)
    WHERE bi.game_id = sample_game_id
      AND (
          ci.api_id = sample_base_item_type_id
          OR ci.base_item_type_id = sample_base_item_type_id
      );

    IF api_item_id <> base_item_id THEN
        RAISE EXCEPTION 'Legacy and base identifiers resolved to different items';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE contype = 'f'
          AND NOT convalidated
    ) THEN
        RAISE EXCEPTION 'One or more foreign keys are not validated';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM service_cache WHERE service_name = 'PriceFetch_Currency'
    ) OR NOT EXISTS (
        SELECT 1 FROM service_cache WHERE service_name = 'CurrencyExchange'
    ) THEN
        RAISE EXCEPTION 'A required CDN worker cursor is missing';
    END IF;
END
$$;
