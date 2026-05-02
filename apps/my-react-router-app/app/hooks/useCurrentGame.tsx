import { useParams } from "react-router";

export default function useCurrentGame(): number {
  const values = useParams();
  const realmId = values.realmId;
  return realmId === "poe2" ? 2 : 1;
}
