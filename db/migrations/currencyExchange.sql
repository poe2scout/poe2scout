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