import { type RouteConfig, index, route } from "@react-router/dev/routes";

export default [
  index("./routes/home.tsx"),
  route("privacy", "./routes/privacy.tsx"),

  route(":realmId/:leagueId", "./routes/:realmId/:leagueId/layout.tsx", [
    index("./routes/:realmId/:leagueId/index.tsx"),
    route("exchange", "./routes/:realmId/:leagueId/exchange.tsx"),

    route("economy", "./routes/:realmId/:leagueId/economy/layout.tsx", [
      index("./routes/:realmId/:leagueId/economy/index.tsx"),
      route(
        "currencies/:category",
        "./routes/:realmId/:leagueId/economy/currencies/:category/index.tsx",
      ),
      route(
        "uniques/:category",
        "./routes/:realmId/:leagueId/economy/uniques/:category/index.tsx",
      ),
    ]),
  ]),
] satisfies RouteConfig;
