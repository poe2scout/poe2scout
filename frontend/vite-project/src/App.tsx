import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ThemeProvider, createTheme, CssBaseline } from "@mui/material";
import Layout from "./components/Layout";
import LandingPage from "./pages/LandingPage";
import EconomyPage from "./pages/EconomyPage";
import { LanguageProvider } from "./contexts/LanguageContext";
import { version } from "../package.json";
import CacheBuster from "react-cache-buster";
import { LeagueProvider } from "./contexts/LeagueContext";
import fetchIntercept from 'fetch-intercept';
import { CategoryProvider } from './contexts/CategoryContext';

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

  return (
    <CacheBuster
      currentVersion={version}
      isEnabled={true}
      isVerboseMode={false}
    >
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
    </CacheBuster>
  );
}

export default App;
