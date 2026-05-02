import { NavLink } from "react-router";

export default function NavLinkButton({
  route,
  children,
  filled = true,
}: {
  route: string;
  children: React.ReactNode;
  filled?: boolean;
}) {
  return (
    <NavLink
      to={route}
      className={`rounded-md border border-secondary px-5 py-2.5 text-center uppercase ${
        filled
          ? "bg-secondary text-gray-950"
          : "bg-transparent text-secondary hover:bg-secondary/10"
      }`}
    >
      <span className="truncate">{children}</span>
      <span aria-hidden="true" className="leading-none font-normal">
        &rarr;
      </span>
    </NavLink>
  );
}
