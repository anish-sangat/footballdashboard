# Football Analytics Dashboard

A Streamlit web app that shows team and player performance as interactive charts,
compares two players, and writes short text insights. The league and season are set
in `config.py` (currently Premier League 2023-24).

## Features
- Sidebar filters: season, team, player, venue (home/away)
- Tabs: Overview, Top Performers, Team Analysis, Player Comparison, Insights
- Radar chart (percentiles) and bar charts to compare two players

## Setup and run
Needs Python 3.11 or newer.

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

To rebuild the clean data from the raw files:

```
python -m src.clean_data
```

## Run the tests
```
pip install pytest
python -m pytest
```

## Project structure
```
app.py              page layout, sidebar, tabs
config.py           settings (league, season, paths, thresholds)
src/clean_data.py   raw files -> clean files (run once)
src/load_data.py    read, cache and filter the clean files
src/charts.py       Plotly figures
src/insights.py     text insights
data/raw/           original files, unchanged
data/clean/         cleaned files used by the app
data/team_names.csv club name fixes (raw name -> standard name)
tests/              pytest tests
```

## Data source
Fantasy Premier League data 2023-24 by Vaastav Anand,
https://github.com/vaastav/Fantasy-Premier-League (MIT License).