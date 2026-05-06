import { type RouteConfig, index, relative, route } from "@react-router/dev/routes";

const league = relative("./routes/:realmId/:leagueId");
const economy = relative("./routes/:realmId/:leagueId/economy");

export default [
  index("./routes/home.tsx"),
  route("privacy", "./routes/privacy.tsx"),

  league.route(":realmId/:leagueId", "layout.tsx", [
    league.index("index.tsx"),
    league.route("exchange", "exchange.tsx"),

    economy.route("economy", "layout.tsx", [
      economy.index("index.tsx"),
      economy.route("currencies/:category", "currencies/:category/index.tsx"),
      economy.route("uniques/:category", "uniques/:category/index.tsx"),
    ]),
  ]),
] satisfies RouteConfig;