"""Tests for the cleaning step. They compare the clean data with the raw files."""
import pandas as pd

from config import RAW_DIR
from src import clean_data


def get_clean_tables():
    log = []
    matches = clean_data.clean_matches(log)
    team_matches = clean_data.make_team_matches(matches)
    players = clean_data.clean_players(log)
    return matches, team_matches, players


def test_every_match_is_kept():
    matches, _, _ = get_clean_tables()
    raw_fixtures = pd.read_csv(RAW_DIR / "fixtures.csv")
    assert len(matches) == len(raw_fixtures)


def test_each_club_has_one_name():
    lookup = clean_data.get_team_lookup()
    assert len(set(lookup.values())) == len(lookup)


def test_wins_draws_losses_add_up_to_matches_played():
    _, team_matches, _ = get_clean_tables()
    number_of_teams = team_matches["Team"].nunique()
    matches_per_team = 2 * (number_of_teams - 1)       # every team plays all others twice
    for team, rows in team_matches.groupby("Team"):
        wins = (rows["Result"] == "W").sum()
        draws = (rows["Result"] == "D").sum()
        losses = (rows["Result"] == "L").sum()
        assert wins + draws + losses == matches_per_team, team


def test_total_goals_match_raw_file():
    matches, _, _ = get_clean_tables()
    raw = pd.read_csv(RAW_DIR / "fixtures.csv")
    raw_goals = raw["team_h_score"].sum() + raw["team_a_score"].sum()
    assert matches["FTHG"].sum() + matches["FTAG"].sum() == raw_goals


def test_top_scorer_goals_match_raw_file():
    _, _, players = get_clean_tables()
    raw = pd.read_csv(RAW_DIR / "players_raw.csv")
    assert players["Goals"].max() == raw["goals_scored"].max()