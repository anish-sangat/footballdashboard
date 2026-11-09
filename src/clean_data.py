"""Turns the raw files in data/raw/ into clean files in data/clean/.

Run once from the project folder:
    python -m src.clean_data
"""
import numpy as np
import pandas as pd

from config import CLEAN_DIR, RAW_DIR, SEASON, TEAM_NAMES_FILE, POSITIONS


def get_team_lookup():
    """Return a dictionary: team id -> standard team name."""
    teams = pd.read_csv(RAW_DIR / "teams.csv")
    names = teams["name"]

    # Fix names with the lookup file, if there is one (FR-03)
    if TEAM_NAMES_FILE.exists():
        fixes = pd.read_csv(TEAM_NAMES_FILE)
        names = names.replace(dict(zip(fixes["raw_name"], fixes["standard_name"])))

    return dict(zip(teams["id"], names))


def clean_matches(log):
    """One row per match, with the columns from section 4.1 of the SRS."""
    fixtures = pd.read_csv(RAW_DIR / "fixtures.csv")
    team_lookup = get_team_lookup()

    matches = pd.DataFrame({
        "Season": SEASON,
        "Date": pd.to_datetime(fixtures["kickoff_time"]).dt.tz_localize(None),
        "HomeTeam": fixtures["team_h"].map(team_lookup),
        "AwayTeam": fixtures["team_a"].map(team_lookup),
        "FTHG": pd.to_numeric(fixtures["team_h_score"], errors="coerce"),
        "FTAG": pd.to_numeric(fixtures["team_a_score"], errors="coerce"),
    })

    # DR-02: drop rows with missing values
    before = len(matches)
    matches = matches.dropna()
    log.append(f"Matches: dropped {before - len(matches)} rows with missing values")

    # DR-03: remove duplicates
    before = len(matches)
    matches = matches.drop_duplicates()
    log.append(f"Matches: dropped {before - len(matches)} duplicate rows")

    # DR-04: goals as whole numbers
    matches["FTHG"] = matches["FTHG"].astype(int)
    matches["FTAG"] = matches["FTAG"].astype(int)

    # Result: H = home win, D = draw, A = away win
    matches["FTR"] = np.where(matches["FTHG"] > matches["FTAG"], "H",
                              np.where(matches["FTHG"] < matches["FTAG"], "A", "D"))

    # DR-06: total goals must equal the raw total
    raw_goals = fixtures["team_h_score"].sum() + fixtures["team_a_score"].sum()
    clean_goals = matches["FTHG"].sum() + matches["FTAG"].sum()
    log.append(f"Goal check: raw={int(raw_goals)}, clean={int(clean_goals)}")
    assert raw_goals == clean_goals, "Goal totals do not match the raw file!"

    return matches.sort_values("Date").reset_index(drop=True)


def make_team_matches(matches):
    """Two rows per match (one for each team) with result and points (FR-04)."""
    home = pd.DataFrame({
        "Season": matches["Season"], "Date": matches["Date"],
        "Team": matches["HomeTeam"], "Opponent": matches["AwayTeam"],
        "Venue": "Home", "GF": matches["FTHG"], "GA": matches["FTAG"],
    })
    away = pd.DataFrame({
        "Season": matches["Season"], "Date": matches["Date"],
        "Team": matches["AwayTeam"], "Opponent": matches["HomeTeam"],
        "Venue": "Away", "GF": matches["FTAG"], "GA": matches["FTHG"],
    })
    rows = pd.concat([home, away]).sort_values(["Season", "Team", "Date"])

    rows["Result"] = np.where(rows["GF"] > rows["GA"], "W",
                              np.where(rows["GF"] < rows["GA"], "L", "D"))
    rows["Points"] = rows["Result"].map({"W": 3, "D": 1, "L": 0})
    rows["GD"] = rows["GF"] - rows["GA"]
    rows["Match_No"] = rows.groupby(["Season", "Team"]).cumcount() + 1
    return rows.reset_index(drop=True)


def clean_players(log):
    """One row per player, with per-90 values (FR-04)."""
    raw = pd.read_csv(RAW_DIR / "players_raw.csv")
    team_lookup = get_team_lookup()

    players = pd.DataFrame({
        "Season": SEASON,
        "Player": raw["first_name"] + " " + raw["second_name"],
        "Team": raw["team"].map(team_lookup),
        "Position": raw["element_type"].map(POSITIONS),
        "Starts": raw["starts"],
        "Minutes": raw["minutes"],
        "Goals": raw["goals_scored"],
        "Assists": raw["assists"],
        "YellowCards": raw["yellow_cards"],
        "RedCards": raw["red_cards"],
        "xG": raw["expected_goals"],
        "xA": raw["expected_assists"],
        "Creativity": raw["creativity"],
        "Threat": raw["threat"],
        "Influence": raw["influence"],
    })

    # DR-04: make sure number columns are numbers, not text
    number_columns = players.columns.drop(["Season", "Player", "Team", "Position"])
    for column in number_columns:
        players[column] = pd.to_numeric(players[column], errors="coerce")

    # DR-02: drop rows with missing important values
    before = len(players)
    players = players.dropna(subset=["Player", "Team", "Position", "Minutes", "Goals"])
    log.append(f"Players: dropped {before - len(players)} rows with missing values")

    # Players with 0 minutes never played, and we cannot divide by 0 for per-90
    before = len(players)
    players = players[players["Minutes"] > 0]
    log.append(f"Players: dropped {before - len(players)} players with 0 minutes")

    # DR-03: duplicates
    before = len(players)
    players = players.drop_duplicates()
    log.append(f"Players: dropped {before - len(players)} duplicate rows")

    # Player names must be unique: add the team to names that appear twice
    is_duplicate = players["Player"].duplicated(keep=False)
    players.loc[is_duplicate, "Player"] = (
        players.loc[is_duplicate, "Player"] + " (" + players.loc[is_duplicate, "Team"] + ")"
    )

    # Per-90 statistics = value / minutes * 90
    per_90_columns = {
        "Goals": "Goals_p90", "Assists": "Assists_p90", "xG": "xG_p90",
        "xA": "xA_p90", "Creativity": "Creativity_p90",
        "Threat": "Threat_p90", "Influence": "Influence_p90",
    }
    for column, new_column in per_90_columns.items():
        players[new_column] = players[column] / players["Minutes"] * 90

    return players.reset_index(drop=True)


def main():
    """Clean everything and save the files."""
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    log = []

    matches = clean_matches(log)
    team_matches = make_team_matches(matches)
    players = clean_players(log)

    matches.to_csv(CLEAN_DIR / "matches.csv", index=False)
    team_matches.to_csv(CLEAN_DIR / "team_matches.csv", index=False)
    players.to_csv(CLEAN_DIR / "players.csv", index=False)

    log.append(f"Saved: {len(matches)} matches, {len(players)} players")
    (CLEAN_DIR / "cleaning_log.txt").write_text("\n".join(log))
    print("\n".join(log))


if __name__ == "__main__":
    main()