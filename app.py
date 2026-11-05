import streamlit as st
import pandas as pd

st.title("Football Dashboard")

data = {
    "Team": ["Arsenal", "Liverpool", "Man City"],
    "Points": [70, 68, 66],
}
df = pd.DataFrame(data)

st.dataframe(df)