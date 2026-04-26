import { NavLink } from "react-router";

export default function NavLinkButton({routeName, routePath}: {routeName: string, routePath: string}) {
  return (
    <NavLink 
      to={routePath} 
      className="mt-2.5 inline-flex items-center justify-center gap-2.5 rounded-md bg-secondary px-5 py-2.5 uppercase text-gray-950"
    >
      <span>{routeName}</span>
      <span aria-hidden="true" className="font-normal leading-none">&rarr;</span>
    </NavLink>
  )
}