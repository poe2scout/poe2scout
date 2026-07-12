import type { Route } from "./+types/home";
import { useState } from "react";
import type { Realm } from "~/features/league/types";
import Section from "~/shared/components/section/section";
import RealmOptions from "../components/realm-options";
import LeagueOptions from "../components/league-options";
import { createPageMeta, SITE_NAME } from "~/shared/meta/page-title";

export function meta({}: Route.MetaArgs) {
  return createPageMeta({
    title: SITE_NAME,
    description:
      "Track Path of Exile 2 market prices, currency exchange rates, and item price history.",
  });
}

export default function Home() {
  const [realm, setRealm] = useState<Realm | null>(null);

  return (
    <div className="flex w-full flex-col gap-4 py-4">
      <Section>
        <h1 className="text-2xl font-semibold tracking-tight text-white">
          POE2 Scout
        </h1>
        <p className="mt-1 max-w-2xl text-sm text-white/60">
          Select a realm and league to open market prices, item history, and
          currency exchange data.
        </p>
      </Section>
      <Section className="space-y-5">
        <RealmOptions selectedRealm={realm} setSelectedRealm={setRealm} />
        {realm ? (
          <LeagueOptions realm={realm} />
        ) : (
          <div className="rounded-sm border border-white/10 bg-white/3 px-3 py-4 text-sm text-white/55">
            Choose a realm to see available leagues.
          </div>
        )}
      </Section>
    </div>
  );
}
