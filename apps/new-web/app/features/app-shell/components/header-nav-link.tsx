import { NavLink } from "react-router";

export default function HeaderNavLink({
  route,
  children,
  end = true,
}: {
  route: string;
  children: React.ReactNode;
  end?: boolean;
}) {
  return (
    <NavLink
      className={({ isActive }) => `px-2.5 ${isActive ? "text-primary" : ""}`}
      to={route}
      end={end}
    >
      {children}
    </NavLink>
  );
}
