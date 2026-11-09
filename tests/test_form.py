import pandas as pd

from src import form


def make_rows(results, team="Arsenal", season="2023-24"):
    """Build a small team_matches table from a list of results like ['W', 'D', 'L']."""
    points = {"W": 3, "D": 1, "L": 0}
    return pd.DataFrame({
        "Season": season,
        "Team": team,
        "Date": pd.date_range("2023-08-01", periods=len(results), freq="7D"),
        "Result": results,
        "Points": [points[r] for r in results],
    })


def test_recent_form_returns_last_results_oldest_first():
    rows = make_rows(["W", "W", "D", "L", "W", "D", "L"])
    assert form.recent_form(rows, n=3) == ["W", "D", "L"]


def test_recent_form_with_fewer_matches_than_n():
    rows = make_rows(["W", "D"])
    assert form.recent_form(rows, n=5) == ["W", "D"]


def test_recent_form_sorts_by_date_not_row_order():
    rows = make_rows(["W", "D", "L"]).iloc[::-1]     # rows in reverse order
    assert form.recent_form(rows, n=3) == ["W", "D", "L"]


def test_longest_unbeaten_run():
    rows = make_rows(["W", "D", "W", "L", "W", "L", "D"])
    assert form.longest_unbeaten_run(rows) == 3


def test_longest_unbeaten_run_with_only_losses():
    rows = make_rows(["L", "L"])
    assert form.longest_unbeaten_run(rows) == 0


def test_form_table_ranks_teams_by_form_points():
    table = pd.concat([
        make_rows(["L", "L", "W", "W", "W"], team="Arsenal"),
        make_rows(["W", "D", "D", "L", "L"], team="Chelsea"),
    ])
    result = form.form_table(table, "2023-24", n=3)
    assert list(result["Team"]) == ["Arsenal", "Chelsea"]
    assert list(result["Form points"]) == [9, 1]
    assert result.loc[0, "Form"] == "W W W"


def test_form_table_ignores_other_seasons():
    table = make_rows(["W", "W"], season="2022-23")
    result = form.form_table(table, "2023-24")
    assert result.empty
