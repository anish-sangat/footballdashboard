"""Functions that turn a table into a Plotly figure."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config import (DEFAULT_COLOR, RESULT_COLORS, RADAR_METRICS,
                    PLAYER_A_COLOR, PLAYER_B_COLOR)


def make_color_map(teams):
    """Give every team its own colour. The same team always gets the same colour."""
    palette = px.colors.qualitative.Alphabet
    sorted_teams = sorted(teams)
    return {team: palette[number % len(palette)] for number, team in enumerate(sorted_teams)}


# Top performers

def top_players_chart(players, column, title, color_map):
    """Horizontal bar chart of the top 10 players for one column."""
    top = players.nlargest(10, column).sort_values(column)   # biggest bar ends up on top
    fig = px.bar(
        top, x=column, y="Player", color="Team", orientation="h", text=column,
        color_discrete_map=color_map, title=title,
        hover_data={"Team": True, "Player": False},
    )
    fig.update_layout(xaxis_title=column, yaxis_title="Player", legend_title="Team")
    return fig


# Team analysis

def results_chart(team_df):
    """Stacked bar: wins, draws and losses, split by home and away."""
    counts = team_df.groupby(["Venue", "Result"]).size().reset_index(name="Matches")
    fig = px.bar(
        counts, x="Venue", y="Matches", color="Result", pattern_shape="Result",
        text="Matches", color_discrete_map=RESULT_COLORS,
        category_orders={"Result": ["W", "D", "L"]},
        title="Wins, draws and losses",
    )
    fig.update_layout(xaxis_title="Venue", yaxis_title="Number of matches")
    return fig


def add_score_text(team_df):
    """Add a 'Score' column such as '2-1' for the tooltips."""
    team_df = team_df.copy()
    team_df["Score"] = team_df["GF"].astype(str) + "-" + team_df["GA"].astype(str)
    return team_df


def points_chart(team_df, team, color_map):
    """Line chart of cumulative points."""
    team_df = add_score_text(team_df.sort_values("Date"))
    team_df["Cumulative points"] = team_df["Points"].cumsum()
    team_df["Match number"] = range(1, len(team_df) + 1)
    fig = px.line(
        team_df, x="Match number", y="Cumulative points", markers=True,
        hover_data={"Opponent": True, "Score": True, "Date": "|%d %b %Y"},
        color_discrete_sequence=[color_map.get(team, DEFAULT_COLOR)],
        title="Cumulative points",
    )
    fig.update_layout(xaxis_title="Match number", yaxis_title="Points")
    return fig


def goals_chart(team_df):
    """Grouped bars: goals scored and conceded in every match."""
    team_df = add_score_text(team_df.sort_values("Date"))
    team_df["Match number"] = range(1, len(team_df) + 1)
    long = team_df.melt(
        id_vars=["Match number", "Opponent", "Score", "Date"],
        value_vars=["GF", "GA"], var_name="Type", value_name="Goals",
    )
    long["Type"] = long["Type"].map({"GF": "Scored", "GA": "Conceded"})
    fig = px.bar(
        long, x="Match number", y="Goals", color="Type", pattern_shape="Type",
        barmode="group", hover_data={"Opponent": True, "Score": True, "Date": "|%d %b %Y"},
        color_discrete_map={"Scored": "#2ca02c", "Conceded": "#d62728"},
        title="Goals scored and conceded per match",
    )
    fig.update_layout(xaxis_title="Match number", yaxis_title="Goals")
    return fig


# Player comparison

def get_percentiles(player, pool):
    """For each radar metric: what % of players in the pool are at or below this player."""
    values = []
    for column in RADAR_METRICS.values():
        percentile = (pool[column] <= player[column]).mean() * 100
        values.append(round(percentile, 1))
    return values


def radar_chart(player_a, player_b, pool):
    """Radar chart. Each metric is a percentile from 0 to 100."""
    labels = list(RADAR_METRICS.keys())
    fig = go.Figure()
    styles = [(player_a, PLAYER_A_COLOR, "solid"), (player_b, PLAYER_B_COLOR, "dash")]
    for player, color, dash in styles:
        values = get_percentiles(player, pool)
        fig.add_trace(go.Scatterpolar(
            r=values + values[:1],            # repeat the first point to close the shape
            theta=labels + labels[:1],
            name=player["Player"], fill="toself", opacity=0.5,
            line=dict(color=color, dash=dash),
        ))
    fig.update_layout(
        title="Percentile among players (0 to 100)",
        polar=dict(radialaxis=dict(range=[0, 100], visible=True)),
    )
    return fig


def compare_bars_chart(player_a, player_b):
    """One small bar chart per metric, showing the raw values of both players."""
    rows = []
    for player in (player_a, player_b):
        for label, column in RADAR_METRICS.items():
            rows.append({"Metric": label, "Player": player["Player"],
                         "Value": round(player[column], 2)})
    data = pd.DataFrame(rows)

    fig = px.bar(
        data, x="Player", y="Value", color="Player", pattern_shape="Player",
        facet_col="Metric", facet_col_wrap=4, text="Value",
        color_discrete_sequence=[PLAYER_A_COLOR, PLAYER_B_COLOR],
        title="Raw values",
    )
    fig.update_yaxes(matches=None, showticklabels=True)    # each metric gets its own scale
    fig.update_xaxes(showticklabels=False, title="")
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    return fig