import pandas as pd

from src import export


def test_to_csv_bytes_has_header_and_no_index():
    table = pd.DataFrame({"Team": ["Arsenal"], "Points": [89]})
    data = export.to_csv_bytes(table)
    assert isinstance(data, bytes)
    assert data.decode("utf-8").splitlines() == ["Team,Points", "Arsenal,89"]
