
INSERT INTO "League" ("value") VALUES ('Dawn of the Hunt');
INSERT INTO "League" ("value") VALUES ('HC Dawn of the Hunt');

DO $$ 
DECLARE 
    divineItemId INTEGER;
    exaltedItemId INTEGER;
BEGIN
    SELECT "itemId" INTO divineItemId FROM "CurrencyItem" WHERE "apiId" = 'divine';
    SELECT "itemId" INTO exaltedItemId FROM "CurrencyItem" WHERE "apiId" = 'exalted';

    INSERT INTO "PriceLog" ("itemId", "price", "createdAt", "quantity", "leagueId") VALUES (divineItemId, 30, NOW(), 1, 1);
    INSERT INTO "PriceLog" ("itemId", "price", "createdAt", "quantity", "leagueId") VALUES (divineItemId, 30, NOW(), 1, 2);

    INSERT INTO "PriceLog" ("itemId", "price", "createdAt", "quantity", "leagueId") VALUES (exaltedItemId, 1, NOW(), 1, 1);
    INSERT INTO "PriceLog" ("itemId", "price", "createdAt", "quantity", "leagueId") VALUES (exaltedItemId, 1, NOW(), 1, 2);

END $$;

CREATE INDEX "idx_pricelog_item_league_created" ON "PriceLog" ("itemId", "leagueId", "createdAt" DESC);