import type { League } from "~/features/league/types";
import formatNumber from "~/shared/utils/format-number";
import type { ExchangeSnapshot } from "../types";
import formatEpoch from "../utils/format-epoch";

export default function ExchangeSummary({
  league,
  snapshot,
}: {
  league: League;
  snapshot: ExchangeSnapshot;
}) {
  return (
    <section className="rounded-sm border border-secondary/35 bg-zinc-950 p-4 shadow-lg shadow-black/30">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-white">
            {league.value} Market
          </h1>
          <p className="mt-1 text-sm text-white/60">
            Last updated {formatEpoch(snapshot.epoch)}
          </p>
        </div>
        <div className="grid gap-3 sm:grid-cols-2">
          <StatBox
            title="Hourly Volume"
            value={snapshot.volume}
            currencyText={snapshot.baseCurrencyText}
            currencyIconUrl={getBaseCurrencyIconUrl(league, snapshot)}
          />
          <StatBox
            title="Market Cap"
            value={snapshot.marketCap}
            currencyText={snapshot.baseCurrencyText}
            currencyIconUrl={getBaseCurrencyIconUrl(league, snapshot)}
          />
        </div>
      </div>
    </section>
  );
}

function StatBox({
  title,
  value,
  currencyText,
  currencyIconUrl,
}: {
  title: string;
  value: number;
  currencyText: string;
  currencyIconUrl: string | null;
}) {
  return (
    <div className="min-w-48 rounded-sm border border-white/10 bg-white/3 px-3 py-2">
      <div className="text-xs font-medium tracking-wide text-white/50 uppercase">
        {title}
      </div>
      <div className="mt-1 flex items-center justify-end gap-1.5 text-lg text-white">
        <span>{formatNumber(value)}</span>
        {currencyIconUrl ? (
          <img
            src={currencyIconUrl}
            alt={currencyText}
            className="h-5 w-5 object-contain"
          />
        ) : (
          <span className="text-sm text-white/60">{currencyText}</span>
        )}
      </div>
    </div>
  );
}

function getBaseCurrencyIconUrl(
  league: League,
  snapshot: ExchangeSnapshot,
): string | null {
  switch (snapshot.baseCurrencyApiId) {
    case league.baseCurrencyApiId:
      return league.baseCurrencyIconUrl;
    case "exalted":
      return league.exaltedCurrencyIconUrl;
    case "divine":
      return league.divineCurrencyIconUrl;
    case "chaos":
      return league.chaosCurrencyIconUrl;
    default:
      return null;
  }
}
