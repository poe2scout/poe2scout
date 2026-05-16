import { useEffect, useRef, useState } from "react";

const ADSENSE_CLIENT_ID = "ca-pub-1450769283178899";
const DEFAULT_ADSENSE_SLOT_ID = "7986001189";

type AdSenseFormat = "auto" | "fluid" | "horizontal" | "vertical";

declare global {
  interface Window {
    adsbygoogle?: Array<Record<string, never>>;
  }
}

export default function AdSenseAd({
  format = "auto",
  className = "",
  layout,
  onFilledChange,
  slotId = DEFAULT_ADSENSE_SLOT_ID,
}: {
  format?: AdSenseFormat;
  className?: string;
  layout?: string;
  onFilledChange?: (isFilled: boolean) => void;
  slotId?: string;
}) {
  const adRef = useRef<HTMLModElement | null>(null);
  const [isUnfilled, setIsUnfilled] = useState(false);
  const [isFilled, setIsFilled] = useState(false);

  useEffect(() => {
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
  }, []);

  useEffect(() => {
    const adElement = adRef.current;

    if (!adElement) return;

    const updateStatus = () => {
      const isAdUnfilled = adElement.dataset.adStatus === "unfilled";
      const isAdFilled =
        !isAdUnfilled &&
        (adElement.dataset.adStatus === "filled" ||
          (adElement.dataset.adsbygoogleStatus === "done" &&
            adElement.querySelector("iframe") !== null));

      setIsUnfilled(isAdUnfilled);
      setIsFilled(isAdFilled);
      onFilledChange?.(isAdFilled);
    };
    const observer = new MutationObserver(updateStatus);

    updateStatus();
    observer.observe(adElement, {
      attributes: true,
      attributeFilter: ["data-ad-status", "data-adsbygoogle-status"],
      childList: true,
      subtree: true,
    });

    return () => observer.disconnect();
  }, [onFilledChange]);

  return (
    <div
      className={`poe2scout-ad ${isFilled ? "poe2scout-ad--filled" : "poe2scout-ad--pending"} ${isUnfilled ? "poe2scout-ad--unfilled" : ""} ${className}`}
      aria-hidden="true"
    >
      <ins
        ref={adRef}
        className="adsbygoogle"
        style={{ display: "block", textAlign: "center" }}
        data-ad-client={ADSENSE_CLIENT_ID}
        data-ad-slot={slotId}
        data-ad-layout={layout}
        data-ad-format={format}
        data-full-width-responsive={format === "fluid" ? undefined : "true"}
      />
    </div>
  );
}
