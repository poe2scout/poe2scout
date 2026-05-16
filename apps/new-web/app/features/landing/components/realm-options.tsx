import { useQuery } from "@tanstack/react-query";
import getRealmsQueryOptions from "~/features/league/queries/realms";
import type { Realm } from "~/features/league/types";
import Loading from "~/shared/components/loading";
import SectionTitle from "~/shared/components/section/section-title";

export default function RealmSelector({
  setSelectedRealm,
  selectedRealm,
}: {
  selectedRealm: Realm | null;
  setSelectedRealm: (realm: Realm) => void;
}) {
  const { data, isPending } = useQuery(getRealmsQueryOptions());

  if (isPending) {
    return (
      <div className="flex min-h-20 items-center justify-center">
        <Loading />
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div>
        <SectionTitle>Realm</SectionTitle>
        <p className="mt-1 text-sm text-white/55">
          Choose the trade realm you want to inspect.
        </p>
      </div>
      <div className="flex flex-wrap gap-2">
        {data?.map((realm) => (
          <button
            type="button"
            key={`${realm.gameApiId}-${realm.realmApiId}`}
            aria-pressed={realm.realmApiId === selectedRealm?.realmApiId}
            onClick={() => setSelectedRealm(realm)}
            className="min-h-10 rounded-sm border border-secondary/35 bg-transparent px-3 py-2 text-sm text-white/80 transition outline-none hover:bg-secondary/10 hover:text-white focus:border-secondary focus:ring-2 focus:ring-secondary/25 aria-pressed:bg-secondary/90 aria-pressed:text-gray-950"
          >
            {realm.gameApiId}/{realm.realmApiId}
          </button>
        ))}
      </div>
    </div>
  );
}
