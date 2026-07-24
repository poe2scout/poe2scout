const footerLinks = [
  { label: "Privacy Policy", href: "/privacy" },
  { label: "Discord", href: "https://discord.gg/EHXVdQCpBq" },
  { label: "GitHub", href: "https://github.com/poe2scout/poe2scout" },
  { label: "API Docs", href: "https://api.poe2scout.com/swagger" },
];

export default function Footer() {
  return (
    <footer className="flex w-full flex-col flex-wrap items-center border-t border-zinc-800/60">
      <section className="flex flex-col items-center gap-3 px-2 py-4">
        <nav className="flex flex-wrap justify-center gap-x-4 gap-y-2">
          {footerLinks.map((link, index) => (
            <span key={link.label} className="inline-flex items-center gap-x-4">
              {index > 0 && (
                <span className="text-zinc-600" aria-hidden="true">
                  |
                </span>
              )}
              <a
                className={
                  "text-zinc-400 transition-colors hover:text-white hover:underline"
                }
                href={link.href}
              >
                {link.label}
              </a>
            </span>
          ))}
        </nav>
      </section>
      <span className="mb-2.5">
        © 2026 POE2 Scout. Not affiliated with Grinding Gear Games.
      </span>
    </footer>
  );
}
