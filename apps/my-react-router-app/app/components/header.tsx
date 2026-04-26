import { NavLink } from "react-router";

export function MyNavLink({ routeName, routePath }: { routeName: string, routePath: string }) {
  return <NavLink className="mx-2.5" to={routePath} end>
    {({ isActive }) => (
           <span className={isActive ? "text-primary" : ""}>{routeName}</span>
         )}
  </NavLink>
}

export default function Header() {
  return <div className="flex w-full flex-row justify-between mt-2.5 text-lg">
    <NavLink className="ml-5 flex" to="/">
      <img className="mx-1.5 w-6 h-6" src="/favicon.ico" alt="poe2scout"/>
      <span>POE2 Scout</span>
    </NavLink>
    <div className="mr-2.5">
      <MyNavLink routeName="Economy" routePath="/Economy"/>
      <MyNavLink routeName="Currency Exchange" routePath="/CurrencyExchange"/>
    </div>
  </ div>;
}
