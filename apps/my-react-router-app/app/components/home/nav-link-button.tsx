import { NavLink } from "react-router";

export default function NavLinkButton({
  route,
  children,
}: {
  route: string;
  children: React.ReactNode;
}) {
  return (
    <NavLink
      to={route}
      className="inline-flex w-full items-center justify-center gap-2.5 rounded-md bg-secondary px-5 py-2.5 text-center text-gray-950 uppercase"
    >
      <span className="truncate">{children}</span>
      <span aria-hidden="true" className="leading-none font-normal">
        &rarr;
      </span>
    </NavLink>
  );
}
