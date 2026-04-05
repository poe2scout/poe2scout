BEGIN;

DO $$
DECLARE
    target_sequence_name constant text := 'currency_exchange_snapshot_pair_id_seq';
    owned_sequence_name text;
BEGIN
    SELECT sequence_ref.relname
    INTO owned_sequence_name
    FROM pg_class AS sequence_ref
    JOIN pg_namespace AS sequence_ns
        ON sequence_ns.oid = sequence_ref.relnamespace
    JOIN pg_depend AS dependency
        ON dependency.objid = sequence_ref.oid
        AND dependency.deptype = 'a'
    JOIN pg_class AS table_ref
        ON table_ref.oid = dependency.refobjid
    JOIN pg_namespace AS table_ns
        ON table_ns.oid = table_ref.relnamespace
    JOIN pg_attribute AS column_ref
        ON column_ref.attrelid = table_ref.oid
        AND column_ref.attnum = dependency.refobjsubid
    WHERE sequence_ref.relkind = 'S'
      AND sequence_ns.nspname = 'public'
      AND table_ns.nspname = 'public'
      AND table_ref.relname = 'currency_exchange_snapshot_pair'
      AND column_ref.attname = 'currency_exchange_snapshot_pair_id';

    IF owned_sequence_name IS NULL THEN
        IF EXISTS (
            SELECT 1
            FROM information_schema.sequences
            WHERE sequence_schema = 'public'
              AND sequence_name = target_sequence_name
        ) THEN
            owned_sequence_name := target_sequence_name;
        ELSE
            RAISE EXCEPTION
                'Could not find a sequence owned by public.currency_exchange_snapshot_pair.currency_exchange_snapshot_pair_id';
        END IF;
    END IF;

    IF owned_sequence_name <> target_sequence_name THEN
        EXECUTE format(
            'ALTER SEQUENCE public.%I RENAME TO %I',
            owned_sequence_name,
            target_sequence_name
        );
    END IF;
END;
$$;

ALTER TABLE public.currency_exchange_snapshot_pair
    ALTER COLUMN currency_exchange_snapshot_pair_id
    SET DEFAULT nextval('public.currency_exchange_snapshot_pair_id_seq'::regclass);

ALTER SEQUENCE public.currency_exchange_snapshot_pair_id_seq
    OWNED BY public.currency_exchange_snapshot_pair.currency_exchange_snapshot_pair_id;

COMMIT;
