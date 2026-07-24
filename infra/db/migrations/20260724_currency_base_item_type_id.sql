BEGIN;

ALTER TABLE currency_item
    ADD COLUMN IF NOT EXISTS base_item_type_id character varying(300);

ALTER TABLE currency_item
    ALTER COLUMN api_id DROP NOT NULL;

ALTER TABLE currency_item
    DROP CONSTRAINT IF EXISTS currency_item_api_id_not_blank,
    DROP CONSTRAINT IF EXISTS currency_item_base_item_type_id_not_blank,
    DROP CONSTRAINT IF EXISTS currency_item_identifier_present;

ALTER TABLE currency_item
    ADD CONSTRAINT currency_item_api_id_not_blank
        CHECK (api_id IS NULL OR api_id !~ '^[[:space:]]*$'),
    ADD CONSTRAINT currency_item_base_item_type_id_not_blank
        CHECK (
            base_item_type_id IS NULL
            OR base_item_type_id !~ '^[[:space:]]*$'
        ),
    ADD CONSTRAINT currency_item_identifier_present
        CHECK (api_id IS NOT NULL OR base_item_type_id IS NOT NULL);

CREATE INDEX IF NOT EXISTS idx_currency_item_base_item_type_id
    ON currency_item (base_item_type_id)
    WHERE base_item_type_id IS NOT NULL;

COMMIT;
