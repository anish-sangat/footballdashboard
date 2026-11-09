"""Tests for insights and charts."""
from config import MIN_MINUTES
from src import charts, insights
from tests.test_clean_data import get_clean_tables


def test_at_least_five_insights():
    matches, team_matches, players = get_clean_tables()
    result = insights.make_insights(matches, team_matches, players)
    assert len(result) >= 5


def test_insights_change_with_filter():
    matches, team_matches, players = get_clean_tables()
    first_team = sorted(team_matches["Team"].unique())[0]

    all_insights = insights.make_insights(matches, team_matches, players)
    one_team = insights.make_insights(
        matches[(matches["HomeTeam"] == first_team) | (matches["AwayTeam"] == first_team)],
        team_matches[team_matches["Team"] == first_team],
        players[players["Team"] == first_team],
    )
    assert all_insights != one_team


def test_radar_values_between_0_and_100():
    _, _, players = get_clean_tables()
    pool = players[players["Minutes"] >= MIN_MINUTES]
    for _, player in players.head(50).iterrows():
        values = charts.get_percentiles(player, pool)
        assert all(0 <= value <= 100 for value in values)


def test_each_team_gets_a_colour():
    _, team_matches, _ = get_clean_tables()
    teams = list(team_matches["Team"].unique())
    color_map = charts.make_color_map(teams)
    assert set(color_map.keys()) == set(teams)