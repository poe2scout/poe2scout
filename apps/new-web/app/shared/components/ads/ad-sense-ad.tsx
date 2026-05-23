import { useEffect, useLayoutEffect, useRef, useState } from "react";

const ADSENSE_CLIENT_ID = "ca-pub-1450769283178899";
const ADSENSE_SLOT_ID = "7986001189";

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
  const wrapperRef = useRef<HTMLDivElement | null>(null);
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

  useLayoutEffect(() => {
    const wrapperElement = wrapperRef.current;
    const adElement = adRef.current;

    if (!wrapperElement || !adElement) return;

    const resetWrapperSize = () => {
      wrapperElement.style.width = "";
      wrapperElement.style.height = "";
      wrapperElement.style.minHeight = "";
    };

    const syncWrapperSizeToAdFrame = () => {
      if (adElement.dataset.adStatus === "unfilled") {
        resetWrapperSize();
        return;
      }

      const iframe = adElement.querySelector("iframe");

      if (!iframe) {
        resetWrapperSize();
        return;
      }

      const width = getFrameDimension(iframe, "width");
      const height = getFrameDimension(iframe, "height");

      if (!width || !height) return;

      wrapperElement.style.width = `${width}px`;
      wrapperElement.style.height = `${height}px`;
      wrapperElement.style.minHeight = "0";
    };

    const observer = new MutationObserver(syncWrapperSizeToAdFrame);

    syncWrapperSizeToAdFrame();
    observer.observe(adElement, {
      attributes: true,
      attributeFilter: [
        "data-ad-status",
        "data-adsbygoogle-status",
        "height",
        "style",
        "width",
      ],
      childList: true,
      subtree: true,
    });

    return () => observer.disconnect();
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
      ref={wrapperRef}
      className={`poe2scout-ad ${isFilled ? "poe2scout-ad--filled" : "poe2scout-ad--pending"} ${isUnfilled ? "poe2scout-ad--unfilled" : ""} ${className}`}
      aria-hidden="true"
    >
      <ins
        ref={adRef}
        className="adsbygoogle"
        style={{ display: "block" }}
        data-ad-client={ADSENSE_CLIENT_ID}
        data-ad-slot={ADSENSE_SLOT_ID}
        data-ad-format={format}
        data-full-width-responsive="true"
      />
    </div>
  );
}

function getFrameDimension(
  iframe: HTMLIFrameElement,
  dimension: "height" | "width",
) {
  const rectDimension =
    dimension === "width"
      ? iframe.getBoundingClientRect().width
      : iframe.getBoundingClientRect().height;
  const attributeDimension = getPositivePixelValue(
    iframe.getAttribute(dimension),
  );
  const styleDimension = getPositivePixelValue(iframe.style[dimension]);

  return attributeDimension ?? styleDimension ?? rectDimension;
}

function getPositivePixelValue(value: string | null) {
  if (!value || !/^\d+(\.\d+)?(px)?$/.test(value)) return null;

  const parsedValue = Number.parseFloat(value);

  return parsedValue > 0 ? parsedValue : null;
}
