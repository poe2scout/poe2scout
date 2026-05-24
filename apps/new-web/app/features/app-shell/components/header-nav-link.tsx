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
        [
          "flex h-7 items-center rounded-sm px-2.5 text-base leading-none whitespace-nowrap transition-colors",
          "hover:bg-white/8 hover:text-secondary",
          "focus-visible:ring-2 focus-visible:ring-secondary/30 focus-visible:outline-none",
          isActive ? "bg-white/12 text-secondary" : "text-white/90",
        ].join(" ")
      }
      to={route}
      end={end}
      prefetch="intent"
      onClick={onClick}
    >
      {children}
    </NavLink>
  );
}
