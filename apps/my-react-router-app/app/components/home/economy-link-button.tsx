import type Realm from "~/types/realm";
import Button from "../button";

export default function EconomyLinkButton({
  realm,
  onClick,
}: {
  realm: Realm;
  onClick: (realm: Realm) => void;
}) {
  return (
    <Button onClick={() => onClick(realm)}>
      {`${realm.gameApiId} ${realm.realmApiId} economy`}
    </Button>
  );
}
