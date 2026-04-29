import type { Route } from "./+types/home";
import { useState } from "react";
import LeagueOptions from "~/components/home/league-options";
import RealmOptions from "~/components/home/realm-options";
import type Realm from "~/types/realm";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "POE2 Scout" },
    { name: "description", content: "POE2 Scout home page!" },
  ];
}

export default function Home() {
  const [realm, setRealm] = useState<Realm | null>(null);

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
      <div className="container mt-6 flex w-full flex-col items-center rounded-lg bg-blue-950 p-3">
        <RealmOptions selectedRealm={realm} setSelectedRealm={setRealm} />
        {realm && <LeagueOptions realm={realm} />}
      </div>
    </>
  );
}
