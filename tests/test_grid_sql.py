"""Check the grid query logic on a small synthetic trade table (no WRDS needed)."""
import importlib.util
from pathlib import Path

import duckdb

spec = importlib.util.spec_from_file_location(
    "grid", Path(__file__).resolve().parents[1] / "code" / "wrds" / "01_pull_spy_grid.py")
grid = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grid)

con = duckdb.connect()
con.execute("create schema taqmsec")
con.execute("""create table taqmsec.ctm_20180613 (
    time_m time, price double, size int, tr_corr varchar,
    sym_root varchar, sym_suffix varchar, tr_seqnum int)""")
trades = [
    ("09:31:00", 99.0, 100, "00", "SPY", None, 1),
    ("13:44:59", 100.0, 100, "00", "SPY", None, 2),
    ("13:45:00", 101.0, 100, "00", "SPY", None, 3),   # exactly at the grid time, counts
    ("13:46:00", 555.0, 100, "01", "SPY", None, 4),   # corrected trade, dropped
    ("13:47:00", 777.0, 100, "00", "SPY", "X", 5),    # suffix, dropped
    ("13:44:00", 999.0, 100, "00", "QQQ", None, 6),   # other ticker, dropped
    ("13:50:00", 102.0, 100, "00", "SPY", None, 7),
    ("16:00:00", 103.0, 100, "00", "SPY", None, 8),
    ("16:00:05", 104.0, 100, "00", "SPY", None, 9),   # after the close, dropped
]
con.executemany("insert into taqmsec.ctm_20180613 values (?,?,?,?,?,?,?)", trades)

sql = grid.build_sql("taqmsec", "ctm_20180613", grid.DEFAULT_MAP)
df = con.execute(sql).df()
row = grid.to_row("2018-06-13", "taqmsec", df)

assert row["px_0945"] == 99.0, row["px_0945"]
assert row["px_1345"] == 101.0, row["px_1345"]
assert row["px_1400"] == 102.0, row["px_1400"]
assert row["px_1600"] == 103.0, row["px_1600"]
assert row["n5_1345"] == 2, row["n5_1345"]
assert row["n_day"] == 5, row["n_day"]
assert row["first_tm_day"].startswith("09:31"), row["first_tm_day"]
for q in (sql, grid.days_sql("taqmsec"), grid.days_sql("taq")):
    assert "%" not in q, "percent sign in query breaks the WRDS driver"
assert str(grid.out_path("x", "auto", 2019)).endswith("dev/spy_grid_auto_2019.csv")
assert str(grid.out_path("x", "auto", 2020)).endswith("holdout/spy_grid_auto_2020.csv")
print("all checks passed")
