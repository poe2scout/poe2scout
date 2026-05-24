import { useEffect, useRef, useState } from "react";

const ADSENSE_CLIENT_ID = "ca-pub-1450769283178899";
const HORIZONTAL_ADSENSE_SLOT_ID = "2600054279";
const HORIZONTAL_AD_WIDTH = 728;
const HORIZONTAL_AD_HEIGHT = 90;

declare global {
  interface Window {
    adsbygoogle?: Array<Record<string, never>>;
  }
}

export default function HorizontalAd({
  className = "",
}: {
  className?: string;
}) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const adRef = useRef<HTMLModElement | null>(null);

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

  const slotId = HORIZONTAL_ADSENSE_SLOT_ID;

  const adStyle = {
    display: "inline-block",
    width: HORIZONTAL_AD_WIDTH,
    height: HORIZONTAL_AD_HEIGHT,
  };

  return (
    <div
      ref={containerRef}
      className={`poe2scout-ad poe2scout-ad--horizontal ${className}`}
      aria-hidden="true"
    >
      <ins
        ref={adRef}
        className="adsbygoogle"
        style={adStyle}
        data-ad-client={ADSENSE_CLIENT_ID}
        data-ad-slot={slotId}
      />
    </div>
  );
}
