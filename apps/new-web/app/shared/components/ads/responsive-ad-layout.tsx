import type { ReactNode } from "react";
import { useEffect, useState } from "react";
import HorizontalAd from "./horizontal-ad";
import VerticalAd from "./veritcal-ad";

const SIDE_AD_MEDIA_QUERY = "(min-width: 1648px)";

export default function ResponsiveAdLayout({
  children,
  className = "",
}: {
  children: ReactNode;
  className?: string;
}) {
  const showSideAds = useShowSideAds();

  return (
    <div className={`poe2scout-ad-layout ${className}`}>
      {!showSideAds && (
        <div className={`poe2scout-ad-layout__inline-ad`}>
          <HorizontalAd className="w-full" />
        </div>
      )}

      {children}

      {showSideAds && (
        <>
          <aside className="poe2scout-ad-layout__side-ad poe2scout-ad-layout__side-ad--left">
            <VerticalAd className="min-h-150 w-40" />
          </aside>
          <aside className="poe2scout-ad-layout__side-ad poe2scout-ad-layout__side-ad--right">
            <VerticalAd className="min-h-150 w-40" />
          </aside>
        </>
      )}
    </div>
  );
}

function useShowSideAds() {
  const [matches, setMatches] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia(SIDE_AD_MEDIA_QUERY);
    const updateMatches = () => setMatches(mediaQuery.matches);

    updateMatches();
    mediaQuery.addEventListener("change", updateMatches);

    return () => mediaQuery.removeEventListener("change", updateMatches);
  }, []);

  return matches;
}
