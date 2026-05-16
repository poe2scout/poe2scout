import {
  isRouteErrorResponse,
  Links,
  Meta,
  Outlet,
  Scripts,
  ScrollRestoration,
  useRouteError,
} from "react-router";

import "./app.css";
import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "./shared/api/query-client";
import GlobalNavigationProgress from "./features/app-shell/components/global-navigation-progress";
import Header from "./features/app-shell/components/header";
import Footer from "./features/app-shell/components/footer";
import NavLinkButton from "./features/landing/components/nav-link-button";

export function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="google-adsense-account" content="ca-pub-1450769283178899" />
        <script
          async
          src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1450769283178899"
          crossOrigin="anonymous"
        />
        <Meta />
        <Links />
      </head>
      <body>
        <GlobalNavigationProgress />
        <Header />
        <main className="mx-auto min-h-dvh w-full max-w-7xl flex-1 px-5">
          {children}
        </main>
        <Footer />
        <ScrollRestoration />
        <Scripts />
      </body>
    </html>
  );
}
export function ErrorBoundary() {
  const error = useRouteError();

  if (isRouteErrorResponse(error) && error.status === 404) {
    return (
      <div className="flex min-h-96 flex-col items-center justify-center gap-4 text-center">
        <h1 className="text-4xl font-bold text-white">Page not found</h1>
        <p className="text-gray-300">This page does not exist.</p>
        <NavLinkButton route="/">Home</NavLinkButton>
      </div>
    );
  }

  return (
    <div className="flex min-h-96 flex-col items-center justify-center gap-4 text-center">
      <h1 className="text-4xl font-bold text-white">Something went wrong</h1>
      <p className="text-gray-300">
        Please try again or return to the home page.
      </p>
    </div>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Outlet />
    </QueryClientProvider>
  );
}
