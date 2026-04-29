import { type RouteConfig, index, prefix, route } from "@react-router/dev/routes";

export default [
  index("./routes/home.tsx"),
  route("privacy", "./routes/privacy.tsx"),

  ...prefix(":realmId/:leagueId", [
      index("./routes/:realmId/:leagueId/index.tsx"),
      route("exchange", "./routes/:realmId/:leagueId/exchange.tsx"),
      route("economy", "./routes/:realmId/:leagueId/economy.tsx")
    ])
  ,
] satisfies RouteConfig;
