import { NavLink } from "react-router";

export default function HeaderNavLink({
  route,
  children,
  end = true,
  onClick,
}: {
  route: string;
  children: React.ReactNode;
  end?: boolean;
  onClick?: () => void;
}) {
  return (
    <NavLink
      className={({ isActive }) =>
        `block whitespace-nowrap px-2.5 py-1 md:py-0 ${isActive ? "text-primary" : ""}`
      }
      to={route}
      end={end}
      onClick={onClick}
    >
      {children}
    </NavLink>
  );
}
