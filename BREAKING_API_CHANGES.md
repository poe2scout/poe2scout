# Breaking API Changes

## Global changes

- Routes, parameter names, and response field names were normalized toward PascalCase across the API. Those case-only changes are not enumerated below.
- League selection was moved from the `league` query parameter into the `{LeagueName}` path parameter on most league-specific endpoints.
- Some resource selectors moved from path parameters into query parameters. Most notably: `{category}` became `?Category=...` on category-based unique and currency endpoints.
- A few previously untyped responses are now explicitly typed in the OpenAPI spec.

## Endpoint: Categories

Old route: `GET /items/categories`
New route: `GET /Items/Categories`

Path parameter changes:
None

Query parameter changes:
None

Response body changes:
(changed) `UniqueCategories[].id` => `UniqueCategories[].ItemCategoryId`
(changed) `CurrencyCategories[].id` => `CurrencyCategories[].CurrencyCategoryId`

## Endpoint: Leagues

Old route: `GET /leagues`
New route: `GET /Leagues`

Path parameter changes:
None

Query parameter changes:
None

Response body changes:
None

## Endpoint: Landing Splash Info

Old route: `GET /items/landingSplashInfo`
New route: `GET /Static/LandingSplashInfo`

Path parameter changes:
None

Query parameter changes:
None

Response body changes:
(changed) `Items[].id` => `Items[].CurrencyItemId`

## Endpoint: Filters

Old route: `GET /items/filters`
New route: `GET /Static/Filters`

Path parameter changes:
None

Query parameter changes:
None

Response body changes:
(changed) previously undocumented / untyped `200` response => `GetFiltersResponse`
(new) `Filters[]`
(new) `Filters[].DisplayName`
(new) `Filters[].Category`
(new) `Filters[].Identifier`

## Endpoint: All Items

Old route: `GET /items`
New route: `GET /Leagues/{LeagueName}/Items`

Path parameter changes:
(new) `LeagueName: string`

Query parameter changes:
(removed) `league: string`

Response body changes:
(changed) `[]` item type changed from `UniqueItemResponse | CurrencyItemResponse` => `GetItemsResponse`
(new) `[].Text`
(new) `[].Name`
(new) `[].Type`
(new) `[].ApiId`

## Endpoint: Item History

Old route: `GET /items/{itemId}/history`
New route: `GET /Leagues/{LeagueName}/Items/{ItemId}/History`

Path parameter changes:
(new) `LeagueName: string`

Query parameter changes:
(removed) `league: string`

Response body changes:
(changed) previously undocumented / untyped `200` response => `GetPriceHistoryResponse`
(new) `PriceHistory[]`
(new) `PriceHistory[].Price`
(new) `PriceHistory[].Time`
(new) `PriceHistory[].Quantity`
(new) `HasMore`

## Endpoint: Currency By Id

Old route: `GET /items/currencyById/{apiId}`
New route: `GET /Leagues/{LeagueName}/Currencies/{ApiId}`

Path parameter changes:
(new) `LeagueName: string`

Query parameter changes:
(removed) `league: string`

Response body changes:
(removed) `item`
(changed) `item.id` => `CurrencyItemId`

## Endpoint: Currency By Category

Old route: `GET /items/currency/{category}`
New route: `GET /Leagues/{LeagueName}/Currencies/ByCategory`

Path parameter changes:
(new) `LeagueName: string`
(removed) `category: string`

Query parameter changes:
(new) `Category: string`
(removed) `league: string`

Response body changes:
(changed) `Items[].id` => `Items[].CurrencyItemId`

## Endpoint: Unique By Category

Old route: `GET /items/unique/{category}`
New route: `GET /Leagues/{LeagueName}/Uniques/ByCategory`

Path parameter changes:
(new) `LeagueName: string`
(removed) `category: string`

Query parameter changes:
(new) `Category: string`
(removed) `league: string`

Response body changes:
(changed) `Items[].id` => `Items[].UniqueItemId`

## Endpoint: Exchange Snapshot

Old route: `GET /currencyExchangeSnapshot`
New route: `GET /Leagues/{LeagueName}/ExchangeSnapshot`

Path parameter changes:
(new) `LeagueName: string`

Query parameter changes:
(removed) `league: string`

Response body changes:
(changed) response schema renamed `GetCurrencyExchangeModel` => `GetExchangeSnapshotResponse`
(changed) `MarketCap` remains a string but now has explicit numeric-string validation
(changed) `Volume` remains a string but now has explicit numeric-string validation

## Endpoint: Snapshot History

Old route: `GET /currencyExchange/SnapshotHistory`
New route: `GET /Leagues/{LeagueName}/SnapshotHistory`

Path parameter changes:
(new) `LeagueName: string`

Query parameter changes:
(removed) `league: string`
(changed) `endTime` => `EndEpoch`

Response body changes:
(changed) `Data[].MarketCap: number` => `Data[].MarketCap: string`
(changed) `Data[].Volume: number` => `Data[].Volume: string`
(changed) `Meta` from a free-form object => explicit object
(new) `Meta.HasMore`

## Endpoint: Snapshot Pairs

Old route: `GET /currencyExchange/SnapshotPairs`
New route: `GET /Leagues/{LeagueName}/SnapshotPairs`

Path parameter changes:
(new) `LeagueName: string`

Query parameter changes:
(removed) `league: string`

Response body changes:
(changed) `[].CurrencyOne.id` => `[].CurrencyOne.CurrencyItemId`
(changed) `[].CurrencyTwo.id` => `[].CurrencyTwo.CurrencyItemId`

## Endpoint: Pair History

Old route: `GET /currencyExchange/PairHistory`
New route: `GET /Leagues/{LeagueName}/Currencies/Pairs/{CurrencyOneItemId}/{CurrencyTwoItemId}/History`

Path parameter changes:
(new) `LeagueName: string`
(new) `CurrencyOneItemId: integer`
(new) `CurrencyTwoItemId: integer`

Query parameter changes:
(removed) `league: string`
(removed) `currencyOneItemId: integer`
(removed) `currencyTwoItemId: integer`

Response body changes:
(changed) `Meta` from a free-form object => explicit object
(new) `Meta.HasMore`

## Endpoint: Added Item Price Histories

Old route: None
New route: `GET /Leagues/{LeagueName}/Items/PriceHistory`

Path parameter changes:
(new) `LeagueName: string`

Query parameter changes:
None

Response body changes:
(new) `ItemHistories[]`
(new) `ItemHistories[].ItemId`
(new) `ItemHistories[].History[]`
(new) `ItemHistories[].History[].Price`
(new) `ItemHistories[].History[].Time`
(new) `ItemHistories[].History[].Quantity`
