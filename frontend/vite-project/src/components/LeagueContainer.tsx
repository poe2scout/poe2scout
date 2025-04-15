
import { styled } from "@mui/material/styles";
import { useLeague } from "../contexts/LeagueContext";
import { FormControl, Select, MenuItem, InputLabel } from "@mui/material";
import translations from "../translationskrmapping.json";
import { CATEGORY_MAPPING } from "../constants";
import { useLanguage } from "../contexts/LanguageContext";
import { Fragment } from "react/jsx-runtime";

const LeagueSelect = styled(Select)(() => ({
    ".MuiSelect-select": {
      padding: "4px 8px",
      fontSize: "0.9rem",
    },
    ".MuiOutlinedInput-notchedOutline": {
      borderColor: "rgba(255, 255, 255, 0.23)",
    },
    "&:hover .MuiOutlinedInput-notchedOutline": {
      borderColor: "rgba(255, 255, 255, 0.4)",  
    },
  }));
const Container = styled("div")({
    padding: "8px 16px",
  });

function LeagueContainer() {
    const { league, setLeague, leagues, loading } = useLeague();
    const { language } = useLanguage();

    if (loading) {
        return <Fragment />;
    }

    const getTranslatedText = (key: string) => {
        if (language === "ko" && key in translations) {
          return translations[key as keyof typeof translations];
        }
        return CATEGORY_MAPPING[key] || key;
      };
    
    const handleLeagueChange = (newLeagueValue: string) => {
        const newLeague = leagues.find(l => l.value === newLeagueValue);
        if (!newLeague) return;

        setLeague(newLeague);
    };



    return (
    <Container>
        <FormControl size="small" fullWidth>
            <InputLabel id="league-select-label">
                {getTranslatedText("League")}
            </InputLabel>
            <LeagueSelect
                labelId="league-select-label"
                id="league-select"
                value={league.value}
                label="League"
                onChange={(e) => handleLeagueChange(e.target.value as string)}
            >
                {leagues.map((leagueOption) => (
                <MenuItem key={leagueOption.value} value={leagueOption.value}>
                    {getTranslatedText(leagueOption.value)}
                </MenuItem>
                ))}
            </LeagueSelect>
        </FormControl>
    </Container>
    )
}

export default LeagueContainer;