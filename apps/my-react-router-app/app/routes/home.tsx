import type { Route } from "./+types/home";
import NavLinkButton from "~/components/nav-link-button";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "POE2 Scout" },
    { name: "description", content: "POE2 Scout home page!" },
  ];
}

export default function Home() {
  return (
    <>
      <span className="mb-2.5 text-center text-7xl font-bold">Poe2 Scout</span>
      <span className="mb-7 text-center text-2xl">
        Your Ultimate Path of Exile 2 Companion
      </span>
      <span className="text-center text-base">
        Track market prices of items, currency, and more with up-to-date Path of
        Exile 2 data
      </span>
      <NavLinkButton route="/pc/economy">View poe 1 pc economy</NavLinkButton>
      <NavLinkButton route="/sony/economy">
        View poe 1 xbox economy
      </NavLinkButton>
      <NavLinkButton route="/xbox/economy">
        View poe 1 sony economy
      </NavLinkButton>
      <NavLinkButton route="/poe2/economy">View POE2 economy</NavLinkButton>
    </>
  );
}
