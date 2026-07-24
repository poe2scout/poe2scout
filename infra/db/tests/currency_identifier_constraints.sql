\set ON_ERROR_STOP on

BEGIN;

DO $$
DECLARE
    target_currency_item_id integer;
BEGIN
    SELECT currency_item_id
    INTO STRICT target_currency_item_id
    FROM currency_item
    ORDER BY currency_item_id
    LIMIT 1;

    UPDATE currency_item
    SET api_id = 'migration-test-api-only',
        base_item_type_id = NULL
    WHERE currency_item_id = target_currency_item_id;

    UPDATE currency_item
    SET api_id = NULL,
        base_item_type_id = 'Metadata/MigrationTest/BaseOnly'
    WHERE currency_item_id = target_currency_item_id;

    UPDATE currency_item
    SET api_id = 'migration-test-both',
        base_item_type_id = 'Metadata/MigrationTest/Both'
    WHERE currency_item_id = target_currency_item_id;

    BEGIN
        UPDATE currency_item
        SET api_id = '',
            base_item_type_id = 'Metadata/MigrationTest/BlankApi'
        WHERE currency_item_id = target_currency_item_id;
        RAISE EXCEPTION 'blank api_id unexpectedly passed validation';
    EXCEPTION
        WHEN check_violation THEN NULL;
    END;

    BEGIN
        UPDATE currency_item
        SET api_id = 'migration-test-blank-base',
            base_item_type_id = ' '
        WHERE currency_item_id = target_currency_item_id;
        RAISE EXCEPTION 'blank base_item_type_id unexpectedly passed validation';
    EXCEPTION
        WHEN check_violation THEN NULL;
    END;

    BEGIN
        UPDATE currency_item
        SET api_id = E'\t',
            base_item_type_id = 'Metadata/MigrationTest/WhitespaceApi'
        WHERE currency_item_id = target_currency_item_id;
        RAISE EXCEPTION 'whitespace-only api_id unexpectedly passed validation';
    EXCEPTION
        WHEN check_violation THEN NULL;
    END;

    BEGIN
        UPDATE currency_item
        SET api_id = 'migration-test-whitespace-base',
            base_item_type_id = E'\n'
        WHERE currency_item_id = target_currency_item_id;
        RAISE EXCEPTION 'whitespace-only base_item_type_id unexpectedly passed validation';
    EXCEPTION
        WHEN check_violation THEN NULL;
    END;

    BEGIN
        UPDATE currency_item
        SET api_id = NULL,
            base_item_type_id = NULL
        WHERE currency_item_id = target_currency_item_id;
        RAISE EXCEPTION 'both-null identifiers unexpectedly passed validation';
    EXCEPTION
        WHEN check_violation THEN NULL;
    END;
END
$$;

ROLLBACK;
