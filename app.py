"""Football Analytics Dashboard. Run with:  streamlit run app.py"""
import streamlit as st

from config import (LEAGUE, ALL_TEAMS, ALL_PLAYERS, NO_DATA_MESSAGE,
                    MIN_MINUTES, DATA_SOURCE)
from src import charts, insights, load_data

st.set_page_config(page_title="Football Analytics Dashboard", page_icon="⚽", layout="wide")
st.title(f"⚽ {LEAGUE} Analytics Dashboard")

# 1. Load data (show a message, not a crash, if something is wrong)
try:
    matches, team_matches, players = load_data.load_all()
except Exception as error:
    st.error(f"Could not load the data. {error}")
    st.stop()

# 2. Sidebar filters
st.sidebar.header("Filters")

seasons = sorted(matches["Season"].unique())
if len(seasons) > 1:
    season = st.sidebar.selectbox("Season", seasons)
else:
    season = seasons[0]            # only one season, so the filter is hidden
    st.sidebar.caption(f"Season: {season}")

team_list = sorted(team_matches[team_matches["Season"] == season]["Team"].unique())
team = st.sidebar.selectbox("Team", [ALL_TEAMS] + team_list)
color_map = charts.make_color_map(team_list)     # one colour per team, same on every chart

# Player filter only shows players of the chosen team (cascading)
players_in_team = load_data.filter_players(players, season, team)
player_list = sorted(players_in_team["Player"])
selected_player = st.sidebar.selectbox("Player", [ALL_PLAYERS] + player_list)

venue = st.sidebar.radio("Venue (team analysis)", ["All", "Home", "Away"])

# 3. Apply the filters
selected_matches = load_data.filter_matches(matches, season, team, venue)
selected_team_rows = load_data.filter_team_matches(team_matches, season, team, venue)

if selected_matches.empty:
    st.warning(NO_DATA_MESSAGE)
    st.stop()

# 4. Tabs
tab_overview, tab_top, tab_team, tab_compare, tab_insights = st.tabs(
    ["Overview", "Top Performers", "Team Analysis", "Player Comparison", "Insights"]
)

# Overview
with tab_overview:
    # League table of the whole season (all teams), using the venue filter
    league_rows = load_data.filter_team_matches(team_matches, season, ALL_TEAMS, venue)
    league_table = load_data.make_league_table(league_rows)
    best_team = league_table.iloc[0]

    total_goals = int(selected_matches["FTHG"].sum() + selected_matches["FTAG"].sum())
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Matches played", len(selected_matches))
    col2.metric("Teams", selected_team_rows["Team"].nunique())
    col3.metric("Total goals", total_goals)
    col4.metric("Avg goals per match", f"{total_goals / len(selected_matches):.2f}")
    col5.metric("Most successful team", best_team["Team"], f"{best_team['Points']} points")

    st.subheader("League table")
    st.dataframe(league_table, hide_index=True, width="stretch")

# Top performers
with tab_top:
    if players_in_team.empty:
        st.info(NO_DATA_MESSAGE)
    else:
        # Show the selected player's numbers, if one is chosen in the sidebar
        if selected_player != ALL_PLAYERS:
            row = players_in_team[players_in_team["Player"] == selected_player].iloc[0]
            st.subheader(f"{row['Player']} ({row['Team']}, {row['Position']})")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Goals", row["Goals"])
            c2.metric("Assists", row["Assists"])
            c3.metric("Minutes", row["Minutes"])
            c4.metric("Starts", row["Starts"])

        table_columns = ["Player", "Team", "Position", "Goals", "Assists", "Minutes"]
        left, right = st.columns(2)
        with left:
            st.plotly_chart(charts.top_players_chart(players_in_team, "Goals", "Top 10 goal scorers", color_map),
                            width="stretch")
            st.caption("Full ranking (click a column header to sort)")
            st.dataframe(players_in_team.sort_values("Goals", ascending=False)[table_columns],
                         hide_index=True, width="stretch")
        with right:
            st.plotly_chart(charts.top_players_chart(players_in_team, "Assists", "Top 10 assist providers", color_map),
                            width="stretch")
            st.caption("Full ranking (click a column header to sort)")
            st.dataframe(players_in_team.sort_values("Assists", ascending=False)[table_columns],
                         hide_index=True, width="stretch")

# Team analysis
with tab_team:
    if team == ALL_TEAMS:
        st.info("Choose a team in the sidebar to see its results, points and goals.")
    elif selected_team_rows.empty:
        st.info(NO_DATA_MESSAGE)
    else:
        st.subheader(team)
        st.plotly_chart(charts.results_chart(selected_team_rows), width="stretch")
        st.plotly_chart(charts.points_chart(selected_team_rows, team, color_map), width="stretch")
        st.plotly_chart(charts.goals_chart(selected_team_rows), width="stretch")

# Player comparison
with tab_compare:
    season_players = players[players["Season"] == season]
    names = list(season_players.sort_values("Goals", ascending=False)["Player"])

    pick_a, pick_b = st.columns(2)
    name_a = pick_a.selectbox("Player A", names, index=0)
    names_for_b = [name for name in names if name != name_a]     # cannot pick the same player
    name_b = pick_b.selectbox("Player B", names_for_b, index=0)

    player_a = season_players[season_players["Player"] == name_a].iloc[0]
    player_b = season_players[season_players["Player"] == name_b].iloc[0]

    # Basic info beside the charts
    for column, player in ((pick_a, player_a), (pick_b, player_b)):
        column.caption(f"{player['Team']} | {player['Position']} | "
                       f"{player['Starts']} starts | {player['Minutes']} minutes")
        if player["Minutes"] < MIN_MINUTES:
            column.warning(f"{player['Player']} played fewer than {MIN_MINUTES} minutes, "
                           "so per-90 values may be unreliable.")

    # Percentiles are calculated only among players with enough minutes
    pool = season_players[season_players["Minutes"] >= MIN_MINUTES]
    st.plotly_chart(charts.radar_chart(player_a, player_b, pool), width="stretch")
    st.plotly_chart(charts.compare_bars_chart(player_a, player_b), width="stretch")
    st.caption(f"Percentiles use players with at least {MIN_MINUTES} minutes. "
               "Creativity, Threat and Influence are Fantasy Premier League ratings.")

# Insights
with tab_insights:
    # Best home record should not depend on the venue filter, so use all venues here
    team_rows_all_venues = load_data.filter_team_matches(team_matches, season, team, "All")
    insight_list = insights.make_insights(selected_matches, team_rows_all_venues, players_in_team)
    for sentence in insight_list:
        st.info(sentence)

st.divider()
st.caption(DATA_SOURCE)