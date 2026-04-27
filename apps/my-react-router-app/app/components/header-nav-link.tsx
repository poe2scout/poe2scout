import { NavLink } from "react-router";

export default function HeaderNavLink({
  route,
  children,
}: {
  route: string;
  children: React.ReactNode;
}) {
  return (
    <NavLink
      className={({ isActive }) => `px-2.5 ${isActive ? "text-primary" : ""}`}
      to={route}
      end
    >
      {children}
    </NavLink>
  );
}
