import { Navigate, useLocation } from "react-router";

export default function LegacyExchangeRedirect() {
  const location = useLocation();

  return <Navigate to={`/poe2/vaal/exchange${location.search}`} replace />;
}
