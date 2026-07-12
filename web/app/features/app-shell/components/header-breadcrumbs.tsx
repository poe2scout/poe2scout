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

  const compactCrumbs = crumbs.length > 2 ? crumbs.slice(-2) : crumbs;
  const hasHiddenCrumbs = compactCrumbs.length !== crumbs.length;

  const renderCrumb = (
    crumb: BreadcrumbItem,
    index: number,
    isLast: boolean,
    showDivider: boolean,
  ) => (
    <li key={index} className="flex min-w-0 items-center gap-2 leading-7">
      {showDivider && <span className="shrink-0 text-gray-500">/</span>}
      {!isLast && crumb.to ? (
        <NavLink
          to={crumb.to}
          className="min-w-0 truncate text-secondary"
          prefetch="intent"
        >
          {crumb.label}
        </NavLink>
      ) : (
        <span
          className="min-w-0 truncate"
          aria-current={isLast ? "page" : undefined}
        >
          {crumb.label}
        </span>
      )}
    </li>
  );

  return (
    <nav aria-label="Breadcrumb" className="min-w-0 px-2.5 text-base">
      <ol className="hidden min-w-0 items-center gap-2 lg:flex">
        {crumbs.map((crumb, index) => {
          const isLast = index === crumbs.length - 1;

          return renderCrumb(crumb, index, isLast, index > 0);
        })}
      </ol>
      <ol className="flex min-w-0 items-center gap-2 lg:hidden">
        {hasHiddenCrumbs && (
          <li className="flex shrink-0 items-center gap-2">
            <span aria-label="Earlier pages" className="text-gray-500">
              ...
            </span>
            <span className="text-gray-500">/</span>
          </li>
        )}
        {compactCrumbs.map((crumb, index) => {
          const isLast = index === compactCrumbs.length - 1;

          return renderCrumb(crumb, index, isLast, index > 0);
        })}
      </ol>
    </nav>
  );
}
