import HomeLeagueSelector from "~/components/home/home-league-selector";
import type { Route } from "./+types/home";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "POE2 Scout" },
    { name: "description", content: "POE2 Scout home page!" },
  ];
}

export default function Home() {
  return (
    <>
      <span className="mb-2.5 text-center text-7xl font-bold">POE2 Scout</span>
      <span className="mb-7 text-center text-2xl">
        Your Ultimate Path of Exile Companion
      </span>
      <span className="text-center text-base">
        Track market prices of items, currency, and more with up-to-date Path of
        Exile data
      </span>
      <HomeLeagueSelector />
    </>
  );
}
