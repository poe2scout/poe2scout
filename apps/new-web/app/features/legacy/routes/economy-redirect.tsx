import { Navigate, useLocation } from "react-router";

export default function LegacyEconomyRedirect() {
  const location = useLocation();

  return <Navigate to={`/poe2/vaal/economy${location.search}`} replace />;
}
