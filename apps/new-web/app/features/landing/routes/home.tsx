import type { Route } from "./+types/home";
import { useState } from "react";
import type { Realm } from "~/features/league/types";
import Section from "~/shared/components/section/section";
import RealmOptions from "../components/realm-options";
import LeagueOptions from "../components/league-options";
import { SITE_NAME } from "~/shared/meta/page-title";

export function meta({}: Route.MetaArgs) {
  return [
    { title: SITE_NAME },
    {
      name: "description",
      content:
        "Track Path of Exile 2 market prices, currency exchange rates, and item price history.",
    },
  ];
}

export default function Home() {
  const [realm, setRealm] = useState<Realm | null>(null);

  return (
    <div className="mt-3 flex w-full flex-col items-center">
      <span className="mb-2.5 text-center text-7xl font-bold">POE2 Scout</span>
      <span className="mb-7 text-center text-2xl">
        Your Ultimate Path of Exile Companion
      </span>
      <span className="text-center text-base">
        Track market prices of items, currency, and more with up-to-date Path of
        Exile data
      </span>
      <Section>
        <RealmOptions selectedRealm={realm} setSelectedRealm={setRealm} />
        {realm && <LeagueOptions realm={realm} />}
      </Section>
    </div>
  );
}
