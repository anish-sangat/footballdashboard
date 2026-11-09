"""All settings for the project live here (paths, thresholds, colours)."""
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent
RAW_DIR = BASE_DIR / "data" / "raw"
CLEAN_DIR = BASE_DIR / "data" / "clean"
TEAM_NAMES_FILE = BASE_DIR / "data" / "team_names.csv"

# Settings (change these to use another league or season)
LEAGUE = "Premier League"
SEASON = "2023-24"
MIN_MINUTES = 450          # players below this are not used for radar percentiles
ALL_TEAMS = "All teams"
ALL_PLAYERS = "All players"
NO_DATA_MESSAGE = "No data for this selection."

# Data source (shown in the app footer)
DATA_SOURCE = (
    f"Data: Fantasy {LEAGUE} data {SEASON} by Vaastav Anand "
    "(github.com/vaastav/Fantasy-Premier-League), MIT License."
)

# FPL position number -> position group
POSITIONS = {1: "GK", 2: "DF", 3: "MF", 4: "FW"}

# Columns each cleaned file must have (used for the error check, FR-02)
MATCH_COLUMNS = ["Season", "Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR"]
TEAM_MATCH_COLUMNS = ["Season", "Date", "Team", "Opponent", "Venue",
                      "GF", "GA", "Result", "Points", "Match_No"]
PLAYER_COLUMNS = ["Season", "Player", "Team", "Position", "Starts", "Minutes",
                  "Goals", "Assists", "Goals_p90", "Assists_p90"]

# Radar chart metrics: label -> column
RADAR_METRICS = {
    "Goals per 90": "Goals_p90",
    "Assists per 90": "Assists_p90",
    "Expected goals per 90": "xG_p90",
    "Expected assists per 90": "xA_p90",
    "Creativity per 90": "Creativity_p90",
    "Threat per 90": "Threat_p90",
    "Influence per 90": "Influence_p90",
}

# Colours
PLAYER_A_COLOR = "#1f77b4"   # blue
PLAYER_B_COLOR = "#ff7f0e"   # orange
RESULT_COLORS = {"W": "#2ca02c", "D": "#999999", "L": "#d62728"}
DEFAULT_COLOR = "#888888"