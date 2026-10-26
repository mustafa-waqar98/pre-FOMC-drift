"""Check the futures grid logic on a few synthetic minute bars (no Databento needed)."""
import importlib.util
from pathlib import Path

import pandas as pd

spec = importlib.util.spec_from_file_location(
    "es", Path(__file__).resolve().parents[1] / "code" / "databento" / "01_es_grid.py")
es = importlib.util.module_from_spec(spec)
spec.loader.exec_module(es)

bars = [  # Eastern stamp, close, contract id
    ("2018-06-12 18:30", 90.0, 1),    # evening of the day before, belongs to June 12
    ("2018-06-13 00:10", 95.0, 1),
    ("2018-06-13 09:44", 99.0, 1),
    ("2018-06-13 13:43", 100.0, 1),
    ("2018-06-13 13:44", 101.0, 1),   # covers 13:44 to 13:45, counts for T = 13:45
    ("2018-06-13 13:45", 102.0, 1),   # starts at 13:45, must not count for T = 13:45
    ("2018-06-13 13:59", 103.0, 1),
    ("2018-06-13 15:59", 109.0, 2),
    ("2018-06-13 16:00", 110.0, 2),   # starts at the close, must not count for T = 16:00
]
idx = pd.DatetimeIndex([pd.Timestamp(t, tz="America/New_York") for t, _, _ in bars]).tz_convert("UTC")
df = pd.DataFrame({"close": [c for _, c, _ in bars], "instrument_id": [i for _, _, i in bars]}, index=idx)

g = es.build_grid(df).set_index("date")
r = g.loc["2018-06-13"]
assert r["px_0945"] == 99.0, r["px_0945"]
assert r["px_1345"] == 101.0 and r["tm_1345"] == "13:44", (r["px_1345"], r["tm_1345"])
assert r["px_1400"] == 103.0, r["px_1400"]
assert r["px_1600"] == 109.0 and r["iid_1600"] == 2 and r["iid_1345"] == 1
assert r["nb5_1345"] == 2, r["nb5_1345"]
assert r["nb5_1200"] == 0, r["nb5_1200"]
assert "2018-06-12" in g.index
print("all checks passed")
