"""Recent form and streaks for teams (uses the team_matches table)."""
import pandas as pd


def recent_form(team_rows, n=5):
    """Last n results of one team, oldest first. Example: ['W', 'D', 'L', 'W', 'W']."""
    last = team_rows.sort_values("Date").tail(n)
    return list(last["Result"])


def longest_unbeaten_run(team_rows):
    """Longest streak of matches without a loss (wins and draws count)."""
    longest = 0
    current = 0
    for result in team_rows.sort_values("Date")["Result"]:
        if result == "L":
            current = 0
        else:
            current += 1
            longest = max(longest, current)
    return longest


def form_table(team_matches, season, n=5):
    """One row per team: its last n results and the points from them."""
    data = team_matches[team_matches["Season"] == season]
    rows = []
    for team, group in data.groupby("Team"):
        last = group.sort_values("Date").tail(n)
        rows.append({
            "Team": team,
            "Form": " ".join(last["Result"]),
            "Form points": int(last["Points"].sum()),
        })
    table = pd.DataFrame(rows, columns=["Team", "Form", "Form points"])
    table = table.sort_values(["Form points", "Team"], ascending=[False, True])
    return table.reset_index(drop=True)
