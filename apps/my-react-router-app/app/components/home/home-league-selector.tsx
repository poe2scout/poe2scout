import type Realm from "~/types/realm";
import { useState } from "react";
import RealmOptions from "./realm-options";
import LeagueOptions from "./league-options";

export default function HomeLeagueSelector() {
  const [realm, setRealm] = useState<Realm | null>(null);

  return (
    <div className="container mt-5 flex w-full flex-col items-center justify-center rounded-lg bg-blue-950 p-5">
      <RealmOptions setSelectedRealm={setRealm} />
      {realm && <LeagueOptions realm={realm} />}
    </div>
  );
}
