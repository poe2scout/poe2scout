import type { Route } from "./+types/privacy";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Privacy Policy | POE2 Scout" },
    { name: "description", content: "POE2 Scout privacy policy." },
  ];
}

export default function Privacy() {
  return (
    <div className="w-full max-w-3xl px-2">
      <h1 className="mb-4 text-3xl font-semibold">Privacy Policy</h1>
      <p className="mb-6 text-sm text-gray-400">Last updated: April 26, 2026</p>

      <section className="mb-6">
        <p>
          We gather and use certain information about users in order to provide
          services and enable certain functions on this website. Personal
          information such as your email address are used for communications
          requested by you and will not be released or sold to third parties.
        </p>
      </section>

      <section className="mb-6">
        <p>
          The poe2scout website may contain adverts or sponsored links on some
          pages. These adverts or sponsored links are typically served either
          through our advertising partner Google Adsense or are self served.
          Poe2scout does not have control of the specific adverts displayed by
          our advertising partners.
        </p>
      </section>

      <section className="mb-6">
        <p>
          A cookie is a small text file stored in your browser. Cookies may be
          used on this website to store your preferences or for analysis of web
          traffic. Cookies may be in use by third party sites linked from this
          website.
        </p>
      </section>

      <section className="mb-6">
        <p>
          You can set your browser to disable cookies, however this may affect
          operation of certain features of this website.
        </p>
      </section>
    </div>
  );
}
