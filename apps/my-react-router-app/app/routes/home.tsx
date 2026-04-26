import type { Route } from "./+types/home";
import NavLinkButton from "~/components/nav-link-button";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "POE2 Scout" },
    { name: "description", content: "POE2 Scout home page!" },
  ];
} 


export default function Home() {
  return <>
      <span className="text-7xl text-center mb-2.5 font-bold">
        Poe2 Scout
      </span>
      <span className="text-2xl text-center mb-7">
        Your Ultimate Path of Exile 2 Companion 
      </span>
      <span className="text-center text-base">
        Track market prices of items, currency, and more with up-to-date Path of Exile 2 data 
      </span>
      <NavLinkButton routeName="View economy" routePath="/Economy"/>
    </>
;
}
