import {
  type RouteConfig,
  index,
  relative,
  route,
} from "@react-router/dev/routes";

const landing = relative("app/features/landing/routes");
const league = relative("app/features/league/routes");
const economy = relative("app/features/economy/routes");
const exchange = relative("app/features/exchange/routes");
const legacy = relative("app/features/legacy/routes");

export default [
  landing.index("./home.tsx"),
  landing.route("privacy", "./privacy.tsx"),

  legacy.route(
    "exchange/pair/:currencyOneItemId/:currencyTwoItemId",
    "./exchange-pair-redirect.tsx",
  ),
  legacy.route("exchange", "./exchange-index-redirect.tsx"),
  legacy.route("exchange/*", "./exchange-redirect.tsx"),
  legacy.route("economy", "./economy-index-redirect.tsx"),
  legacy.route("economy/*", "./economy-redirect.tsx"),

  league.route(":realmId/:leagueId", "./layout.tsx", [
    league.index("./index.tsx"),
    exchange.route("exchange", "./exchange.tsx"),
    exchange.route(
      "exchange/pair/:currencyOneItemId/:currencyTwoItemId",
      "./pair-history.tsx",
    ),
    economy.route("economy", "./layout.tsx", [
      economy.index("./index.tsx"),
      economy.route("currencies/:category", "./currencies.tsx"),
      economy.route(
        "currencies/:category/:itemId/:itemName?",
        "./currency-item-detail.tsx",
      ),
      economy.route("uniques/:category", "./uniques.tsx"),
      economy.route(
        "uniques/:category/:itemId/:itemName?",
        "./unique-item-detail.tsx",
      ),
    ]),
  ]),
] satisfies RouteConfig;
