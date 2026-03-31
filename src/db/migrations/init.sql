DROP SCHEMA public CASCADE;
CREATE SCHEMA public;

GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;

CREATE TABLE "ItemCategory" (
  "id" SERIAL PRIMARY KEY,
  "apiId" character varying (300) NOT NULL,
  "label" character varying (300) NOT NULL
);

CREATE TABLE "ItemType" (
  "id" SERIAL PRIMARY KEY,
  "value" character varying (300) NOT NULL,
  "categoryId" integer NOT NULL,
  FOREIGN KEY ("categoryId") REFERENCES "ItemCategory" ("id")
);

CREATE TABLE "BaseItem" (
  "id" SERIAL PRIMARY KEY,
  "typeId" integer NOT NULL,
  "iconUrl" character varying (300),
  "itemMetadata" json,
  FOREIGN KEY ("typeId") REFERENCES "ItemType" ("id")
);

CREATE TABLE "Item" (
  "id" SERIAL PRIMARY KEY,
  "baseItemId" integer NOT NULL,
  "itemType" character varying(50) NOT NULL,
  FOREIGN KEY ("baseItemId") REFERENCES "BaseItem" ("id")
);

CREATE TABLE "UniqueItem" (
  "id" SERIAL PRIMARY KEY,
  "itemId" integer NOT NULL,
  "iconUrl" character varying (300),
  "name" character varying (300),
  "text" character varying (300),
  "itemMetadata" json,
  FOREIGN KEY ("itemId") REFERENCES "Item" ("id")
);


CREATE TABLE "CurrencyCategory" (
  "id" SERIAL PRIMARY KEY,
  "apiId" character varying (300) NOT NULL,
  "label" character varying (300) NOT NULL
);

CREATE TABLE "CurrencyItem" (
  "id" SERIAL PRIMARY KEY,
  "itemId" integer NOT NULL,
  "currencyCategoryId" integer NOT NULL,
  "apiId" character varying (300) NOT NULL,
  "text" character varying (300) NOT NULL,
  "iconUrl" character varying (300),
  "itemMetadata" json,
  FOREIGN KEY ("itemId") REFERENCES "Item" ("id"),
  FOREIGN KEY ("currencyCategoryId") REFERENCES "CurrencyCategory" ("id")
);

CREATE TABLE "League" (
  "id" SERIAL PRIMARY KEY,
  "value" character varying (300) NOT NULL
);

CREATE TABLE "PriceLog" (
  "id" SERIAL PRIMARY KEY,
  "itemId" integer NOT NULL,
  "price" double precision NOT NULL,
  "createdAt" timestamp without time zone NOT NULL,  
  "quantity" integer NOT NULL,
  "leagueId" integer NOT NULL,
  FOREIGN KEY ("itemId") REFERENCES "Item" ("id"),
  FOREIGN KEY ("leagueId") REFERENCES "League" ("id")
);



CREATE INDEX "idx_baseitem_typeId" ON "BaseItem" ("typeId");
CREATE INDEX "idx_item_baseItemId" ON "Item" ("baseItemId");
CREATE INDEX "idx_item_itemType" ON "Item" ("itemType");
CREATE INDEX "idx_pricelog_leagueId" ON "PriceLog" ("leagueId");

