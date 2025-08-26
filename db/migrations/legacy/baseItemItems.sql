INSERT INTO "Item" ("baseItemId", "itemType")
SELECT b."id", 'base'
FROM "BaseItem" b
