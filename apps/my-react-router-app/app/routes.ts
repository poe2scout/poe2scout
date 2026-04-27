import { type RouteConfig, index, prefix, route } from "@react-router/dev/routes";

export default [
  index("./routes/home.tsx"),
  route("privacy", "./routes/privacy.tsx"),

  ...prefix(":realmId/economy", [
    index("./routes/economy/index.tsx"),
    ...prefix(":leagueId", [
      index("./routes/economy/overview.tsx"),
      route("exchange", "./routes/economy/exchange.tsx")
    ])
  ]),
] satisfies RouteConfig;
