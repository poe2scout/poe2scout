import { NavLink, useMatch } from "react-router";
import HeaderNavLink from "./header-nav-link";
import useLeagueParams from "~/hooks/useLeagueParams";
import HeaderBreadcrumbs from "./header-breadcrumbs";

export default function Header() {
  const { isLeagueSelected, realmId, leagueId } = useLeagueParams();
  const leagueHomeMatch = useMatch("/:realmId/:leagueId");
  const isLeagueHome = leagueHomeMatch !== null;

  return (
    <header className="flex w-full flex-col justify-center bg-black py-1.5">
      <div className="mx-auto flex w-full max-w-7xl flex-row justify-between py-2.5 text-lg">
        <div className="ml-5 flex gap-4">
          <NavLink className="flex" to="/">
            <img
              className="mx-1.5 h-6 w-6"
              src="/favicon.ico"
              alt="poe2scout"
            />
            POE2 Scout
          </NavLink>
          {isLeagueSelected && isLeagueHome && (
            <NavLink className="px-2.5" to="/">
              &larr; Select different league
            </NavLink>
          )}
          {isLeagueSelected && !isLeagueHome && <HeaderBreadcrumbs />}
        </div>
        <div className="mr-2.5">
          {isLeagueSelected && (
            <>
              <HeaderNavLink route={`/${realmId}/${leagueId}`}>
                Home
              </HeaderNavLink>
              <HeaderNavLink
                route={`/${realmId}/${leagueId}/economy`}
                end={false}
              >
                Economy
              </HeaderNavLink>
              <HeaderNavLink route={`/${realmId}/${leagueId}/exchange`}>
                Currency Exchange
              </HeaderNavLink>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
