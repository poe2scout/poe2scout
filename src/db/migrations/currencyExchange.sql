CREATE TABLE "CurrencyExchangeSnapshot" (
    "CurrencyExchangeSnapshotId" SERIAL PRIMARY KEY,

    "Epoch" integer NOT NULL,
    "LeagueId" integer NOT NULL,
    "Volume" DECIMAL(20, 8) NULL,
    "MarketCap" DECIMAL(20, 8) NULL,

    FOREIGN KEY ("LeagueId") REFERENCES "League" ("id")
);

CREATE TABLE "CurrencyExchangeSnapshotPair" (
    "CurrencyExchangeSnapshotPairId" SERIAL PRIMARY KEY, 

    "CurrencyExchangeSnapshotId" integer NOT NULL,
    "CurrencyOneId" integer NOT NULL,
    "CurrencyTwoId" integer NOT NULL,

    "Volume" DECIMAL(20, 8) NOT NULL, -- IN EXALTS BASED ON MOST LIQUID CURRENCY IN PAIR

    FOREIGN KEY ("CurrencyExchangeSnapshotId") REFERENCES "CurrencyExchangeSnapshot" ("CurrencyExchangeSnapshotId"),
    FOREIGN KEY ("CurrencyOneId") REFERENCES "Item" ("id"),
    FOREIGN KEY ("CurrencyTwoId") REFERENCES "Item" ("id")
);

CREATE TABLE "CurrencyExchangeSnapshotPairData" (
    "CurrencyExchangeSnapshotPairId" integer NOT NULL,
    "CurrencyId" integer NOT NULL,
    
    "ValueTraded" DECIMAL(20, 8) NOT NULL, -- Exalts value of items traded
    "RelativePrice" DECIMAL(20, 8) NOT NULL, -- Price of item in exalts according to exchange rate with other item
    "StockValue" DECIMAL(20, 8) NOT NULL,

    "VolumeTraded" BIGINT NOT NULL,
    "HighestStock" BIGINT NOT NULL,

    PRIMARY KEY ("CurrencyExchangeSnapshotPairId", "CurrencyId")
);


CREATE TABLE "ServiceCache" (
    "ServiceCacheId" SERIAL PRIMARY KEY,
	"ServiceName" VARCHAR(100) NOT NULL,
    "Value" integer NOT NULL
);




CREATE TABLE public.currency_exchange_history (
    "Epoch" INTEGER NOT NULL,
    "LeagueId" INTEGER,
    "CurrencyExchangeSnapshotPairId" INTEGER NOT NULL,
    "CurrencyOneId" INTEGER,
    "C1_ValueTraded" DECIMAL(20, 8),
    "C1_RelativePrice" DECIMAL(20, 8),
    "C1_StockValue" DECIMAL(20, 8),
    "C1_VolumeTraded" BIGINT,
    "C1_HighestStock" BIGINT,
    "CurrencyTwoId" INTEGER,
    "C2_ValueTraded" DECIMAL(20, 8),
    "C2_RelativePrice" DECIMAL(20, 8),
    "C2_StockValue" DECIMAL(20, 8),
    "C2_VolumeTraded" BIGINT,
    "C2_HighestStock" BIGINT
);


CREATE INDEX idx_currency_history_epoch ON public.currency_exchange_history ("Epoch" DESC);

CREATE INDEX idx_currency_history_snapshotpairid ON public.currency_exchange_history ("CurrencyExchangeSnapshotPairId");

CREATE INDEX idx_currency_history_league_c1_c2 ON public.currency_exchange_history ("LeagueId", "CurrencyOneId", "CurrencyTwoId");


CREATE OR REPLACE FUNCTION initialize_currency_history()
RETURNS void AS $$
BEGIN
    TRUNCATE TABLE public.currency_exchange_history;

    INSERT INTO public.currency_exchange_history
    SELECT
        ces."Epoch",
        ces."LeagueId",
        cesp."CurrencyExchangeSnapshotPairId",
        cesp."CurrencyOneId",
        cespd1."ValueTraded" AS "C1_ValueTraded",
        cespd1."RelativePrice" AS "C1_RelativePrice",
        cespd1."StockValue" AS "C1_StockValue",
        cespd1."VolumeTraded" AS "C1_VolumeTraded",
        cespd1."HighestStock" AS "C1_HighestStock",
        cesp."CurrencyTwoId",
        cespd2."ValueTraded" AS "C2_ValueTraded",
        cespd2."RelativePrice" AS "C2_RelativePrice",
        cespd2."StockValue" AS "C2_StockValue",
        cespd2."VolumeTraded" AS "C2_VolumeTraded",
        cespd2."HighestStock" AS "C2_HighestStock"
    FROM "CurrencyExchangeSnapshot" AS ces
    JOIN "CurrencyExchangeSnapshotPair" AS cesp ON cesp."CurrencyExchangeSnapshotId" = ces."CurrencyExchangeSnapshotId"
    JOIN "CurrencyExchangeSnapshotPairData" AS cespd1 ON cespd1."CurrencyExchangeSnapshotPairId" = cesp."CurrencyExchangeSnapshotPairId" AND cespd1."CurrencyId" = cesp."CurrencyOneId"
    JOIN "CurrencyExchangeSnapshotPairData" AS cespd2 ON cespd2."CurrencyExchangeSnapshotPairId" = cesp."CurrencyExchangeSnapshotPairId" AND cespd2."CurrencyId" = cesp."CurrencyTwoId";
END;
$$ LANGUAGE plpgsql;



CREATE OR REPLACE FUNCTION update_currency_history_incrementally()
RETURNS void AS $$
DECLARE
    last_epoch INTEGER;
BEGIN
    SELECT COALESCE(max("Epoch"), 0) INTO last_epoch FROM public.currency_exchange_history;

    INSERT INTO public.currency_exchange_history
    SELECT
        ces."Epoch",
        ces."LeagueId",
        cesp."CurrencyExchangeSnapshotPairId",
        cesp."CurrencyOneId",
        cespd1."ValueTraded" AS "C1_ValueTraded",
        cespd1."RelativePrice" AS "C1_RelativePrice",
        cespd1."StockValue" AS "C1_StockValue",
        cespd1."VolumeTraded" AS "C1_VolumeTraded",
        cespd1."HighestStock" AS "C1_HighestStock",
        cesp."CurrencyTwoId",
        cespd2."ValueTraded" AS "C2_ValueTraded",
        cespd2."RelativePrice" AS "C2_RelativePrice",
        cespd2."StockValue" AS "C2_StockValue",
        cespd2."VolumeTraded" AS "C2_VolumeTraded",
        cespd2."HighestStock" AS "C2_HighestStock"
    FROM "CurrencyExchangeSnapshot" AS ces
    JOIN "CurrencyExchangeSnapshotPair" AS cesp ON cesp."CurrencyExchangeSnapshotId" = ces."CurrencyExchangeSnapshotId"
    JOIN "CurrencyExchangeSnapshotPairData" AS cespd1 ON cespd1."CurrencyExchangeSnapshotPairId" = cesp."CurrencyExchangeSnapshotPairId" AND cespd1."CurrencyId" = cesp."CurrencyOneId"
    JOIN "CurrencyExchangeSnapshotPairData" AS cespd2 ON cespd2."CurrencyExchangeSnapshotPairId" = cesp."CurrencyExchangeSnapshotPairId" AND cespd2."CurrencyId" = cesp."CurrencyTwoId"
    WHERE ces."Epoch" > last_epoch; 

END;
$$ LANGUAGE plpgsql;

CREATE INDEX ON currency_exchange_history ("LeagueId", "CurrencyOneId", "CurrencyTwoId", "Epoch" DESC);