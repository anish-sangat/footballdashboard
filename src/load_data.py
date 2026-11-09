"""Reads the cleaned files (with caching) and filters them."""
import pandas as pd
import streamlit as st

from config import (CLEAN_DIR, MATCH_COLUMNS, TEAM_MATCH_COLUMNS,
                    PLAYER_COLUMNS, ALL_TEAMS)


def read_file(file_name, required_columns, date_columns=None):
    """Read one CSV file and check that it has the columns we need (FR-02)."""
    path = CLEAN_DIR / file_name
    if not path.exists():
        raise FileNotFoundError(
            f"Data file '{file_name}' was not found in data/clean/. "
            "Run 'python -m src.clean_data' first."
        )
    data = pd.read_csv(path, parse_dates=date_columns or [])
    missing = [col for col in required_columns if col not in data.columns]
    if missing:
        raise ValueError(f"File '{file_name}' is missing columns: {', '.join(missing)}")
    return data


@st.cache_data
def load_all():
    """Load the three clean tables once. Streamlit keeps them in memory (FR-01)."""
    matches = read_file("matches.csv", MATCH_COLUMNS, ["Date"])
    team_matches = read_file("team_matches.csv", TEAM_MATCH_COLUMNS, ["Date"])
    players = read_file("players.csv", PLAYER_COLUMNS)
    return matches, team_matches, players


# Filters

def filter_matches(matches, season, team, venue):
    """Matches of the chosen season, team and venue (one row per match)."""
    data = matches[matches["Season"] == season]
    if team == ALL_TEAMS:
        return data
    if venue == "Home":
        return data[data["HomeTeam"] == team]
    if venue == "Away":
        return data[data["AwayTeam"] == team]
    return data[(data["HomeTeam"] == team) | (data["AwayTeam"] == team)]


def filter_team_matches(team_matches, season, team, venue):
    """Team-match rows (one row per team per match) for the selection."""
    data = team_matches[team_matches["Season"] == season]
    if team != ALL_TEAMS:
        data = data[data["Team"] == team]
    if venue != "All":
        data = data[data["Venue"] == venue]
    return data


def filter_players(players, season, team):
    """Players of the chosen season and team."""
    data = players[players["Season"] == season]
    if team != ALL_TEAMS:
        data = data[data["Team"] == team]
    return data


# League table

def make_league_table(team_matches):
    """Points table. Sorted by points, then goal difference, then goals scored (FR-12)."""
    table = team_matches.groupby("Team").agg(
        Played=("Result", "count"),
        Wins=("Result", lambda r: (r == "W").sum()),
        Draws=("Result", lambda r: (r == "D").sum()),
        Losses=("Result", lambda r: (r == "L").sum()),
        GF=("GF", "sum"),
        GA=("GA", "sum"),
        Points=("Points", "sum"),
    ).reset_index()
    table["GD"] = table["GF"] - table["GA"]
    table = table.sort_values(["Points", "GD", "GF"], ascending=False)
    table.insert(0, "Rank", range(1, len(table) + 1))
    return table.reset_index(drop=True)