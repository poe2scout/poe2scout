import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ThemeProvider, createTheme, CssBaseline } from "@mui/material";
import Layout from "./components/Layout";
import LandingPage from "./pages/LandingPage";
import EconomyPage from "./pages/EconomyPage";
import { LanguageProvider } from "./contexts/LanguageContext";
import { version } from "../package.json";
import { useEffect } from "react";
import { LeagueProvider } from "./contexts/LeagueContext";
import fetchIntercept from 'fetch-intercept';
import { CategoryProvider } from './contexts/CategoryContext';
import { compare } from 'compare-versions';

// Register fetch interceptor
fetchIntercept.register({
    request: function(url, config) {
        if (url.endsWith('/meta.json')) {
            url = `${url}?ver=${Date.now()}`;
        }
        return [url, config];
    }
});

function App() {
    const theme = createTheme({
        palette: {
            mode: "dark",
        },
    });

    useEffect(() => {
        const checkCacheStatus = async () => {
            try {
                const res = await fetch('/meta.json');
                const { version: metaVersion } = await res.json();
                
                const shouldForceRefresh = compare(metaVersion, version, '>');
                if (shouldForceRefresh) {
                    console.log(`There is a new version (v${metaVersion}). Should force refresh.`);
                    
                    if (window?.caches) {
                        const { caches } = window;
                        const cacheNames = await caches.keys();
                        const cacheDeletionPromises = cacheNames.map((n) => caches.delete(n));
                        await Promise.all(cacheDeletionPromises);
                        console.log('The cache has been deleted.');
                    }
                    
                    // @ts-ignore: Firefox still has a `forceReload` parameter.
                    window.location.reload(true);
                } else {
                    console.log('There is no new version. No cache refresh needed.');
                }
            } catch (error) {
                console.error('An error occurred while checking cache status:', error);
            }
        };

        checkCacheStatus();
    }, []);

    return (
        <ThemeProvider theme={theme}>
            <LanguageProvider>
                <LeagueProvider>
                    <CategoryProvider>
                        <CssBaseline />
                        <BrowserRouter>
                            <Routes>
                                <Route path="/" element={<Layout />}>
                                    <Route index element={<LandingPage />} />
                                    <Route path="economy">
                                        <Route
                                            index
                                            element={<Navigate to="/economy/currency" replace />}
                                        />
                                        <Route path=":type" element={<EconomyPage />} />
                                    </Route>
                                    <Route path="*" element={<Navigate to="/" replace />} />
                                </Route>
                            </Routes>
                        </BrowserRouter>
                    </CategoryProvider>
                </LeagueProvider>
            </LanguageProvider>
        </ThemeProvider>
    );
}

export default App;