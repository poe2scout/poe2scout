import type { ReactNode } from "react";
import { NavLink, useMatches } from "react-router";

export type BreadcrumbItem = {
  label: ReactNode;
  to?: string;
};

type BreadcrumbMatch = {
  data: unknown;
  params: Record<string, string | undefined>;
  pathname: string;
};

export type BreadcrumbHandle = {
  breadcrumb?: (
    match: BreadcrumbMatch,
  ) => BreadcrumbItem | BreadcrumbItem[] | null;
};

type BreadcrumbHandleWithBreadcrumb = BreadcrumbHandle & {
  breadcrumb: NonNullable<BreadcrumbHandle["breadcrumb"]>;
};

function hasBreadcrumbHandle(
  handle: unknown,
): handle is BreadcrumbHandleWithBreadcrumb {
  return (
    typeof handle === "object" &&
    handle !== null &&
    "breadcrumb" in handle &&
    typeof (handle as BreadcrumbHandle).breadcrumb === "function"
  );
}

export default function HeaderBreadcrumbs() {
  const matches = useMatches();
  const crumbs = matches.flatMap((match) => {
    if (!hasBreadcrumbHandle(match.handle)) return [];

    const crumb = match.handle.breadcrumb({
      data: match.data,
      params: match.params,
      pathname: match.pathname,
    });

    if (!crumb) return [];
    return Array.isArray(crumb) ? crumb : [crumb];
  });

  if (crumbs.length === 0) return null;

  return (
    <nav aria-label="Breadcrumb" className="px-2.5">
      <ol className="flex items-center gap-2">
        {crumbs.map((crumb, index) => {
          const isLast = index === crumbs.length - 1;

          return (
            <li key={index} className="flex items-center gap-2">
              {index > 0 && <span className="text-gray-500">/</span>}
              {!isLast && crumb.to ? (
                <NavLink to={crumb.to} className="text-secondary">
                  {crumb.label}
                </NavLink>
              ) : (
                <span aria-current={isLast ? "page" : undefined}>
                  {crumb.label}
                </span>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
