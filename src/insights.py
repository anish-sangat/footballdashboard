"""Creates short plain-language sentences from the data."""


def top_scorer(players):
    row = players.loc[players["Goals"].idxmax()]
    return f"Top scorer: {row['Player']} ({row['Team']}) with {row['Goals']} goals."


def top_assister(players):
    row = players.loc[players["Assists"].idxmax()]
    return f"Top assist provider: {row['Player']} ({row['Team']}) with {row['Assists']} assists."


def most_yellow_cards(players):
    row = players.loc[players["YellowCards"].idxmax()]
    return f"Most yellow cards: {row['Player']} ({row['Team']}) with {row['YellowCards']}."


def best_home_record(team_matches):
    home = team_matches[team_matches["Venue"] == "Home"]
    points = home.groupby("Team")["Points"].sum()
    best_team = points.idxmax()
    played = (home["Team"] == best_team).sum()
    return f"Best home record: {best_team} with {points[best_team]} points from {played} home matches."


def highest_scoring_match(matches):
    totals = matches["FTHG"] + matches["FTAG"]
    row = matches.loc[totals.idxmax()]
    date = row["Date"].strftime("%d %b %Y")
    return (f"Highest-scoring match: {row['HomeTeam']} {row['FTHG']}-{row['FTAG']} "
            f"{row['AwayTeam']} on {date} ({totals.max()} goals).")


def average_goals(matches):
    average = (matches["FTHG"] + matches["FTAG"]).mean()
    return f"Average goals per match: {average:.2f}."


def home_win_share(matches):
    share = (matches["FTR"] == "H").mean() * 100
    return f"The home side won {share:.0f}% of the matches."


def make_insights(matches, team_matches, players):
    """Return a list of insight sentences for the current selection."""
    insights = []
    if not players.empty:
        insights += [top_scorer(players), top_assister(players), most_yellow_cards(players)]
    if not team_matches.empty:
        insights.append(best_home_record(team_matches))
    if not matches.empty:
        insights += [highest_scoring_match(matches), average_goals(matches),
                     home_win_share(matches)]
    return insights