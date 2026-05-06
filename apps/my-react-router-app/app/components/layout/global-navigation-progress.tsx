import { useEffect, useState } from "react";
import { useNavigation } from "react-router";

type ProgressPhase = "starting" | "loading" | "complete";

export default function GlobalNavigationProgress(): React.ReactElement | null {
  const navigation = useNavigation();
  const [visible, setVisible] = useState(false);
  const [phase, setPhase] = useState<ProgressPhase>("starting");

  const isRouteLoading =
    navigation.state === "loading" && navigation.location !== undefined;
  const width =
    phase === "complete" ? "w-full" : phase === "loading" ? "w-[88%]" : "w-0";
  const opacity = phase === "complete" ? "opacity-0" : "opacity-100";

  useEffect(() => {
    if (!isRouteLoading) {
      setPhase("complete");

      const hideTimeout = window.setTimeout(() => {
        setVisible(false);
        setPhase("starting");
      }, 260);

      return () => window.clearTimeout(hideTimeout);
    }

    setVisible(true);
    setPhase("starting");

    const loadingTimeout = window.setTimeout(() => {
      setPhase("loading");
    }, 20);

    return () => window.clearTimeout(loadingTimeout);
  }, [isRouteLoading]);

  if (!visible) {
    return null;
  }

  return (
    <div
      aria-hidden="true"
      className="pointer-events-none fixed inset-x-0 top-0 z-50 h-0.5 bg-transparent"
    >
      <div
        className={`h-full bg-red-600 shadow-[0_0_8px_rgba(220,38,38,0.75)] transition-[width,opacity] duration-250 ease-out ${width} ${opacity}`}
      />
    </div>
  );
}
