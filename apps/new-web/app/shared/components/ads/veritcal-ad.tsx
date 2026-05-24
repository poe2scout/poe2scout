import { useEffect, useRef, useState } from "react";

const ADSENSE_CLIENT_ID = "ca-pub-1450769283178899";
const ADSENSE_SLOT_ID = "7986001189";

declare global {
  interface Window {
    adsbygoogle?: Array<Record<string, never>>;
  }
}

export default function VerticalAd({ className = "" }: { className?: string }) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const adRef = useRef<HTMLModElement | null>(null);

  useEffect(() => {
    const adElement = adRef.current;

    if (!adElement) {
      return;
    }

    try {
      window.adsbygoogle = window.adsbygoogle || [];
      window.adsbygoogle.push({});
    } catch (error) {
      if (import.meta.env.DEV) {
        console.warn("AdSense failed to initialize", error);
      }
    }
  }, []);

  const adStyle = { display: "block" };

  return (
    <div
      ref={containerRef}
      className={`poe2scout-ad poe2scout-ad--vertical ${className}`}
      aria-hidden="true"
    >
      <ins
        ref={adRef}
        className="adsbygoogle"
        style={adStyle}
        data-ad-client={ADSENSE_CLIENT_ID}
        data-ad-slot={ADSENSE_SLOT_ID}
        data-ad-format={"vertical"}
        data-full-width-responsive={"true"}
      />
    </div>
  );
}
