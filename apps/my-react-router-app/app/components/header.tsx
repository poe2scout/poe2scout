import { NavLink } from "react-router";
import HeaderNavLink from "./header-nav-link";

export default function Header() {
  return (
    <div className="flex w-full flex-row justify-between py-2.5 text-lg">
      <NavLink className="ml-5 flex" to="/">
        <img className="mx-1.5 h-6 w-6" src="/favicon.ico" alt="poe2scout" />
        POE2 Scout
      </NavLink>
      <div className="mr-2.5">
        <HeaderNavLink route="/economy">Economy</HeaderNavLink>
        <HeaderNavLink route="/exchange">Currency Exchange</HeaderNavLink>
      </div>
    </div>
  );
}
