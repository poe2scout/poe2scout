import { useState } from "react";
import { NavLink, useMatch } from "react-router";
import HeaderNavLink from "./header-nav-link";
import useLeagueParams from "~/features/league/hooks/use-league-params";
import HeaderBreadcrumbs from "./header-breadcrumbs";

export default function Header() {
  const { isLeagueSelected, realmId, leagueId } = useLeagueParams();
  const leagueHomeMatch = useMatch("/:realmId/:leagueId");
  const isLeagueHome = leagueHomeMatch !== null;
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const closeMenu = () => setIsMenuOpen(false);

  const leagueNavigation = isLeagueSelected ? (
    <>
      <HeaderNavLink route={`/${realmId}/${leagueId}`} onClick={closeMenu}>
        Home
      </HeaderNavLink>
      <HeaderNavLink
        route={`/${realmId}/${leagueId}/economy`}
        end={false}
        onClick={closeMenu}
      >
        Economy
      </HeaderNavLink>
      <HeaderNavLink
        route={`/${realmId}/${leagueId}/exchange`}
        end={false}
        onClick={closeMenu}
      >
        Currency Exchange
      </HeaderNavLink>
    </>
  ) : null;

  return (
    <header className="flex w-full flex-col justify-center bg-zinc-900 py-1.5">
      <div className="relative mx-auto flex w-full max-w-7xl flex-row items-center justify-between gap-3 px-4 py-2.5 text-lg sm:px-5">
        <div className="flex min-w-0 flex-1 items-center gap-3">
          <NavLink
            className="flex shrink-0 items-center whitespace-nowrap"
            to="/"
            prefetch="intent"
          >
            <img
              className="mx-1.5 h-6 w-6"
              src="/favicon.ico"
              alt="poe2scout"
            />
            POE2 Scout
          </NavLink>
          {isLeagueSelected && isLeagueHome && (
            <NavLink
              className="min-w-0 truncate px-2.5"
              to="/"
              prefetch="intent"
            >
              &larr; Select different league
            </NavLink>
          )}
          {isLeagueSelected && !isLeagueHome && <HeaderBreadcrumbs />}
        </div>
        {isLeagueSelected && (
          <nav
            aria-label="Primary navigation"
            className="hidden shrink-0 items-center gap-2 md:flex"
          >
            {leagueNavigation}
          </nav>
        )}
        {isLeagueSelected && (
          <div
            className="relative shrink-0 md:hidden"
            onBlur={(event) => {
              if (!event.currentTarget.contains(event.relatedTarget)) {
                closeMenu();
              }
            }}
          >
            <button
              type="button"
              className="flex h-9 w-9 items-center justify-center rounded-sm border border-secondary/40 text-white"
              aria-label={
                isMenuOpen
                  ? "Close primary navigation"
                  : "Open primary navigation"
              }
              aria-expanded={isMenuOpen}
              onClick={() => setIsMenuOpen((open) => !open)}
            >
              <span className="flex w-4 flex-col gap-1" aria-hidden="true">
                <span className="h-0.5 rounded-full bg-current" />
                <span className="h-0.5 rounded-full bg-current" />
                <span className="h-0.5 rounded-full bg-current" />
              </span>
            </button>
            {isMenuOpen && (
              <nav
                aria-label="Primary navigation"
                className="absolute top-11 right-0 z-20 flex min-w-52 flex-col rounded-sm border border-secondary/35 bg-zinc-900 py-2 shadow-lg shadow-black/50"
              >
                {leagueNavigation}
              </nav>
            )}
          </div>
        )}
      </div>
    </header>
  );
}
