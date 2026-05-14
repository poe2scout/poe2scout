import type { TableColumn } from "~/shared/components/table/types";
import type {
  CurrencyEconomyItem,
  CurrencyMetadata,
  EconomyItem,
  ItemMetadata,
  UniqueEconomyItem,
} from "../types";
import type { League, Realm } from "~/features/league/types";

const DIVINE_THRESHOLD = 1.2;

type CurrencyDisplay = {
  label: string;
  iconUrl: string | null;
};

export function getEconomyItemKey(item: EconomyItem) {
  return "uniqueItemId" in item
    ? `unique-${item.uniqueItemId}`
    : `currency-${item.currencyItemId}`;
}

export function getEconomyTableColumns({
  realm,
  league,
  referenceCurrency,
}: {
  realm: Realm;
  league: League;
  referenceCurrency: string;
}): TableColumn<EconomyItem>[] {
  return [
    {
      id: "item",
      header: "Item",
      className: "min-w-72",
      cell: (item) => <ItemCell item={item} />,
    },
    {
      id: "price",
      header: "Price",
      className: "w-36 text-right",
      headerClassName: "w-36 text-right",
      cell: (item) => (
        <PriceCell
          currentPrice={item.currentPrice}
          league={league}
          referenceCurrency={referenceCurrency}
        />
      ),
    },
    {
      id: "quantity",
      header: "Quantity",
      className: "w-28 text-right text-white/80",
      headerClassName: "w-28 text-right",
      cell: (item) => item.currentQuantity?.toLocaleString() ?? "N/A",
    },
    {
      id: "actions",
      header: "Actions",
      className: "w-32 text-center",
      headerClassName: "w-32 text-center",
      cell: (item) => <ActionLinks item={item} league={league} realm={realm} />,
    },
  ];
}

function ItemCell({ item }: { item: EconomyItem }) {
  const isUnique = isUniqueItem(item);
  const name = getItemDisplayName(item);
  const detail = isUnique ? getUniqueDetail(item.itemMetadata) : null;

  return (
    <div className="flex min-w-0 items-center gap-2">
      <img
        src={item.iconUrl ?? undefined}
        alt=""
        className="h-8 w-8 shrink-0 object-contain"
      />
      <div className="min-w-0">
        <div
          className={`truncate ${isUnique ? "text-amber-500" : "text-white"}`}
        >
          {name}
        </div>
        {detail && (
          <div className="truncate text-xs text-white/45">{detail}</div>
        )}
      </div>
    </div>
  );
}

function PriceCell({
  currentPrice,
  league,
  referenceCurrency,
}: {
  currentPrice: number | null;
  league: League;
  referenceCurrency: string;
}) {
  if (currentPrice == null) {
    return <span className="text-white/50">N/A</span>;
  }

  const divinePrice = getDivinePriceForReference(referenceCurrency, league);
  const showInDivine =
    divinePrice > 0 && currentPrice / divinePrice >= DIVINE_THRESHOLD;
  const displayCurrency = getCurrencyDisplay(
    showInDivine ? "divine" : referenceCurrency,
    league,
  );
  const displayPrice = showInDivine ? currentPrice / divinePrice : currentPrice;

  return (
    <div
      className="flex items-center justify-end gap-1.5"
      title={`${formatPrice(currentPrice)} ${getCurrencyDisplay(referenceCurrency, league).label}`}
    >
      <span>{formatPrice(displayPrice)}</span>
      {displayCurrency.iconUrl ? (
        <img
          src={displayCurrency.iconUrl}
          alt={displayCurrency.label}
          className="h-5 w-5 object-contain"
        />
      ) : (
        <span className="text-xs text-white/50">{displayCurrency.label}</span>
      )}
    </div>
  );
}

function ActionLinks({
  item,
  league,
  realm,
}: {
  item: EconomyItem;
  league: League;
  realm: Realm;
}) {
  return (
    <div className="flex justify-center gap-1.5 text-xs">
      <a
        href={getWikiUrl(item, realm)}
        target="_blank"
        rel="noreferrer"
        className="text-white/60 transition hover:text-secondary"
      >
        Wiki
      </a>
      <span className="text-white/25">/</span>
      <a
        href={getTradeUrl(item, league, realm)}
        target="_blank"
        rel="noreferrer"
        className="text-white/60 transition hover:text-secondary"
      >
        Trade
      </a>
    </div>
  );
}

function isUniqueItem(item: EconomyItem): item is UniqueEconomyItem {
  return "uniqueItemId" in item;
}

function isCurrencyItem(item: EconomyItem): item is CurrencyEconomyItem {
  return "currencyItemId" in item;
}

function getItemDisplayName(item: EconomyItem) {
  return isUniqueItem(item) ? item.name : item.text;
}

function getUniqueDetail(metadata: ItemMetadata | CurrencyMetadata | null) {
  if (!metadata) {
    return null;
  }

  return metadata.baseType ?? metadata.name ?? null;
}

function getDivinePriceForReference(referenceCurrency: string, league: League) {
  if (referenceCurrency === "divine") {
    return 1;
  }

  if (referenceCurrency === "chaos") {
    return league.chaosDivinePrice;
  }

  return league.divinePrice;
}

function getCurrencyDisplay(apiId: string, league: League): CurrencyDisplay {
  if (apiId === league.baseCurrencyApiId) {
    return {
      label: league.baseCurrencyText,
      iconUrl: league.baseCurrencyIconUrl,
    };
  }

  switch (apiId) {
    case "exalted":
      return {
        label: league.exaltedCurrencyText,
        iconUrl: league.exaltedCurrencyIconUrl,
      };
    case "divine":
      return {
        label: league.divineCurrencyText,
        iconUrl: league.divineCurrencyIconUrl,
      };
    case "chaos":
      return {
        label: league.chaosCurrencyText,
        iconUrl: league.chaosCurrencyIconUrl,
      };
    default:
      return {
        label: apiId,
        iconUrl: null,
      };
  }
}

function formatPrice(value: number) {
  return value.toLocaleString(undefined, {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  });
}

function getWikiUrl(item: EconomyItem, realm: Realm) {
  const wikiName = encodeURIComponent(getItemDisplayName(item));
  const wikiHost =
    realm.gameApiId === "poe" ? "www.poewiki.net" : "www.poe2wiki.net";

  return `https://${wikiHost}/wiki/${wikiName}`;
}

function getTradeUrl(item: EconomyItem, league: League, realm: Realm) {
  const tradeBaseUrl = `https://www.pathofexile.com/${realm.tradeApiPath}`;
  const encodedLeague = encodeURIComponent(league.value.toLowerCase());

  if (isCurrencyItem(item)) {
    return `${tradeBaseUrl}/exchange/${realm.realmApiId}/${encodedLeague}?q=${encodeURIComponent(
      JSON.stringify({
        exchange: {
          status: { option: "online" },
          have: [league.baseCurrencyApiId],
          want: [item.apiId],
        },
      }),
    )}`;
  }

  return `${tradeBaseUrl}/search/${realm.realmApiId}/${encodedLeague}?q=${encodeURIComponent(
    JSON.stringify({
      query: {
        filters: {},
        name: item.name,
      },
    }),
  )}`;
}
