import { Navigate, useLocation, useParams } from "react-router";

export default function LegacyExchangePairRedirect() {
  const location = useLocation();
  const { currencyOneItemId, currencyTwoItemId } = useParams();

  return (
    <Navigate
      to={`/poe2/vaal/exchange/pair/${currencyOneItemId}/${currencyTwoItemId}${location.search}`}
      replace
    />
  );
}
