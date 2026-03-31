import { useEffect, useState } from "react";
import { BuildInfo, ClassMapping } from "../types";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  CircularProgress,
} from "@mui/material";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Bar } from "react-chartjs-2";
import { useTheme } from "@mui/material/styles";

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const getChartOptions = (theme: any) => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false,
    },
    title: {
      display: true,
      text: "Leaderboard Class Distribution",
      color: theme.palette.text.primary,
      font: {
        size: 32,
      },
    },
  },
  scales: {
    y: {
      grid: {
        color: theme.palette.divider,
      },
      ticks: {
        color: theme.palette.text.primary,
      },
    },
    x: {
      grid: {
        display: false,
      },
      ticks: {
        color: theme.palette.text.primary,
      },
    },
  },
});

export function BuildsPage() {
  const theme = useTheme();
  const [buildData, setBuildData] = useState<BuildInfo[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchBuildData = async () => {
      try {
        const response = await fetch(
          `${import.meta.env.VITE_API_URL}/buildinfo`
        );
        const data = await response.json();
        setBuildData(data);
      } catch (error) {
        console.error("Error fetching build data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchBuildData();
  }, []);

  const chartData = {
    labels: buildData.map((item) => ClassMapping[item.class]),
    datasets: [
      {
        data: buildData.map((item) => item.count),
        backgroundColor: "rgba(75, 192, 192, 0.6)",
        borderColor: "rgba(75, 192, 192, 1)",
        borderWidth: 1,
      },
    ],
  };

  if (loading) {
    return (
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        height="100vh"
      >
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3, maxWidth: "1200px", margin: "0 auto" }}>
      <Typography
        variant="h4"
        component="h1"
        gutterBottom
        sx={{ color: theme.palette.text.primary }}
      ></Typography>

      {/* Chart Section */}
      <Box sx={{ height: "400px", mb: 4 }}>
        <Bar options={getChartOptions(theme)} data={chartData} />
      </Box>

      {/* Class Cards Grid */}
      <Grid container spacing={2}>
        {buildData.map((build) => (
          <Grid item xs={12} sm={6} md={4} lg={3} key={build.class}>
            <Card
              sx={{
                bgcolor:
                  theme.palette.mode === "dark"
                    ? "rgba(255, 255, 255, 0.05)"
                    : "rgba(0, 0, 0, 0.05)",
                backdropFilter: "blur(10px)",
                color: theme.palette.text.primary,
                transition: "transform 0.2s",
                "&:hover": {
                  transform: "translateY(-4px)",
                },
              }}
            >
              <CardContent>
                <Typography variant="h6" component="div">
                  {ClassMapping[build.class]}
                </Typography>
                <Typography
                  sx={{ mb: 1.5 }}
                  color={theme.palette.text.secondary}
                >
                  {(
                    (build.count /
                      buildData.reduce((acc, curr) => acc + curr.count, 0)) *
                    100
                  ).toFixed(1)}
                  % of builds
                </Typography>
                <Typography variant="body2">
                  {build.count} total builds
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}
