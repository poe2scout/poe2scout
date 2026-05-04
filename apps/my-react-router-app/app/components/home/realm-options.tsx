import type Realm from "~/types/realm";
import { useQuery } from "@tanstack/react-query";
import Loading from "../loading";
import getRealmsQueryOptions from "~/api/query-options/realms";
import SectionTitle from "../section-title";
import SectionDivider from "../section-divider";
import SectionContent from "../section-content";

export default function RealmSelector({
  setSelectedRealm,
  selectedRealm,
}: {
  selectedRealm: Realm | null;
  setSelectedRealm: (realm: Realm) => void;
}) {
  const { data, isPending } = useQuery(getRealmsQueryOptions());

  if (isPending) return <Loading />;

  return (
    <>
      <SectionTitle>Select a Realm</SectionTitle>
      <SectionDivider />
      <SectionContent>
        <div className="flex flex-col gap-6 md:flex-row">
          {data &&
            data.map((realm) => (
              <button
                key={`${realm.gameApiId}-${realm.realmApiId}`}
                aria-pressed={realm.realmApiId === selectedRealm?.realmApiId}
                onClick={() => setSelectedRealm(realm)}
                className="my-2.5 items-center rounded-md border border-secondary bg-transparent px-5 py-2.5 text-secondary aria-pressed:bg-secondary aria-pressed:text-gray-950"
              >
                {realm.gameApiId}/{realm.realmApiId} Realm
              </button>
            ))}
        </div>
      </SectionContent>
    </>
  );
}
