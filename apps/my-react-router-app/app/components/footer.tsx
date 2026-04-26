import { Link } from "react-router";

declare global {
  interface Window {
    googlefc?: {
      callbackQueue: Array<() => void>;
      showRevocationMessage: () => void;
    };
  }
}

export default function Footer() {
  function showPrivacySettings() {
    window.googlefc?.callbackQueue.push(window.googlefc.showRevocationMessage);
  }

  return (
    <footer className="flex w-full flex-col flex-wrap items-center">
      <section className="gap-x-4 gap-y-2 px-2 py-4">
        <Link className="mx-5 underline" to="/privacy">
          Privacy Policy
        </Link>
        <button
          className="mx-5 underline"
          type="button"
          onClick={showPrivacySettings}
        >
          Privacy and cookie settings
        </button>
      </section>
      <span className="mb-2.5">
        © 2026 POE2 Scout. Not affiliated with Grinding Gear Games.
      </span>
    </footer>
  );
}
