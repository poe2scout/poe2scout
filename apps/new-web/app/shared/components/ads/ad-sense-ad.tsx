import { useEffect, useRef, useState } from "react";

const ADSENSE_CLIENT_ID = "ca-pub-1450769283178899";
const DEFAULT_ADSENSE_SLOT_ID = "7986001189";
const HORIZONTAL_ADSENSE_SLOT_ID = "2600054279";
const HORIZONTAL_AD_WIDTH = 728;
const HORIZONTAL_AD_HEIGHT = 90;
const AD_REQUEST_TIMEOUT_MS = 4_000;

type AdSenseFormat = "auto" | "horizontal" | "vertical";

declare global {
  interface Window {
    adsbygoogle?: Array<Record<string, never>>;
  }
}

export default function AdSenseAd({
  format = "auto",
  className = "",
  onFilledChange,
}: {
  format?: AdSenseFormat;
  className?: string;
  onFilledChange?: (isFilled: boolean) => void;
}) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const adRef = useRef<HTMLModElement | null>(null);
  const [canRequestAd, setCanRequestAd] = useState(format !== "horizontal");
  const [isUnfilled, setIsUnfilled] = useState(false);
  const [isUnavailable, setIsUnavailable] = useState(false);
  const [isFilled, setIsFilled] = useState(false);

  useEffect(() => {
    if (format !== "horizontal") {
      setCanRequestAd(true);
      return;
    }

    const container = containerRef.current;
    if (!container) return;

    const updateCanRequestAd = () => {
      const hasRequiredWidth = container.clientWidth >= HORIZONTAL_AD_WIDTH;
      setCanRequestAd(hasRequiredWidth);

      if (!hasRequiredWidth) {
        setIsUnfilled(false);
        setIsUnavailable(false);
        setIsFilled(false);
        onFilledChange?.(false);
      }
    };
    const resizeObserver = new ResizeObserver(updateCanRequestAd);

    updateCanRequestAd();
    resizeObserver.observe(container);

    return () => resizeObserver.disconnect();
  }, [format, onFilledChange]);

  useEffect(() => {
    if (!canRequestAd) {
      return;
    }

    const adElement = adRef.current;

    if (!adElement || adElement.dataset.poe2scoutAdRequested === "true") {
      return;
    }

    adElement.dataset.poe2scoutAdRequested = "true";

    try {
      window.adsbygoogle = window.adsbygoogle || [];
      window.adsbygoogle.push({});
    } catch (error) {
      if (import.meta.env.DEV) {
        console.warn("AdSense failed to initialize", error);
      }
    }
  }, [canRequestAd]);

  useEffect(() => {
    if (!canRequestAd) {
      return;
    }

    const adElement = adRef.current;

    if (!adElement) return;

    const hasAdResponse = () =>
      adElement.dataset.adStatus !== undefined ||
      adElement.querySelector("iframe") !== null;

    const updateStatus = () => {
      const isAdUnfilled = adElement.dataset.adStatus === "unfilled";
      const isAdFilled =
        !isAdUnfilled &&
        (adElement.dataset.adStatus === "filled" ||
          (adElement.dataset.adsbygoogleStatus === "done" &&
            adElement.querySelector("iframe") !== null));

      if (hasAdResponse()) {
        window.clearTimeout(timeoutId);
        setIsUnavailable(false);
      }

      setIsUnfilled(isAdUnfilled);
      setIsFilled(isAdFilled);
      onFilledChange?.(isAdFilled);
    };
    const observer = new MutationObserver(updateStatus);
    const timeoutId = window.setTimeout(() => {
      if (hasAdResponse()) {
        return;
      }

      setIsUnavailable(true);
      setIsFilled(false);
      onFilledChange?.(false);
    }, AD_REQUEST_TIMEOUT_MS);

    updateStatus();
    observer.observe(adElement, {
      attributes: true,
      attributeFilter: ["data-ad-status", "data-adsbygoogle-status"],
      childList: true,
      subtree: true,
    });

    return () => {
      window.clearTimeout(timeoutId);
      observer.disconnect();
    };
  }, [canRequestAd, onFilledChange]);

  const isFixedHorizontal = format === "horizontal";
  const slotId = isFixedHorizontal
    ? HORIZONTAL_ADSENSE_SLOT_ID
    : DEFAULT_ADSENSE_SLOT_ID;
  const adStyle = isFixedHorizontal
    ? {
        display: "inline-block",
        width: HORIZONTAL_AD_WIDTH,
        height: HORIZONTAL_AD_HEIGHT,
      }
    : { display: "block" };

  return (
    <div
      ref={containerRef}
      className={`poe2scout-ad poe2scout-ad--${format} ${isFilled ? "poe2scout-ad--filled" : "poe2scout-ad--pending"} ${isUnfilled ? "poe2scout-ad--unfilled" : ""} ${isUnavailable ? "poe2scout-ad--unavailable" : ""} ${className}`}
      aria-hidden="true"
    >
      {canRequestAd && (
        <ins
          ref={adRef}
          className="adsbygoogle"
          style={adStyle}
          data-ad-client={ADSENSE_CLIENT_ID}
          data-ad-slot={slotId}
          data-ad-format={isFixedHorizontal ? undefined : format}
          data-full-width-responsive={isFixedHorizontal ? undefined : "true"}
        />
      )}
    </div>
  );
}
