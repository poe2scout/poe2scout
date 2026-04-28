import useRealms from "~/api/use-realms";
import type Realm from "~/types/realm";
import EconomyLinkButton from "./economy-link-button";

export default function RealmSelector({
  setSelectedRealm,
}: {
  setSelectedRealm: (realm: Realm) => void;
}) {
  const { data, isLoading } = useRealms();

  if (isLoading) {
    return <span>Loading...</span>;
  }

  return (
    <>
      <span className="text-2xl">Select your realm</span>
      <div className="flex w-full flex-col justify-around pt-2.5 md:flex-row">
        {data &&
          data.map((realm) => (
            <EconomyLinkButton
              onClick={setSelectedRealm}
              key={realm.realmApiId}
              realm={realm}
            />
          ))}
      </div>
    </>
  );
}
