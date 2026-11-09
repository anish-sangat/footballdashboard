"""Helpers for downloading tables from the dashboard."""


def to_csv_bytes(table):
    """Turn a DataFrame into CSV bytes for st.download_button."""
    return table.to_csv(index=False).encode("utf-8")
