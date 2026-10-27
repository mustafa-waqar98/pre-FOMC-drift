"""Synthetic-fixture tests for the panel builder."""
import importlib.util
from pathlib import Path

import pandas as pd

spec = importlib.util.spec_from_file_location("pb", Path(__file__).resolve().parents[1] / "code" / "03_build_panel.py")
pb = importlib.util.module_from_spec(spec); spec.loader.exec_module(pb)

K = pb.KEY
def row(date, tm1600="15:59", nb=5, iid=1, empty=False):
    r = {"date": date}
    for k in K:
        r[f"px_{k}"] = None if empty else 100.0
        r[f"tm_{k}"] = tm1600 if k == "1600" else "10:00"
        r[f"iid_{k}"] = iid
        r[f"nb5_{k}"] = nb
    return r

g = pd.DataFrame([row("2018-01-02"), row("2018-01-03", empty=True, nb=0), row("2018-11-23", tm1600="12:59"),
                  row("2018-01-05", nb=0), row("2019-12-31"), row("2020-01-02")])
g["date"] = pd.to_datetime(g["date"])
cut = g[g["date"] <= pb.CUTOFF]
f = pb.flag_grid(cut).set_index("date")
assert len(f) == 4 and pd.Timestamp("2018-01-03") not in f.index          # no-bar day dropped
assert f.loc["2018-11-23", "half_day"] == 1 and f.loc["2018-01-02", "half_day"] == 0
assert f.loc["2018-01-05", "missing_trade"] == 1 and f.loc["2018-01-02", "missing_trade"] == 0

d = lambda col, v: pd.DataFrame({"date": f.index.strftime("%Y-%m-%d"), col: v})
fomc = pd.DataFrame({"decision_date": ["2018-01-02", "2018-01-03", "2018-01-04"],
                     "meeting_type": ["scheduled", "unscheduled", "scheduled"]})
p = pb.merge_all(f.reset_index(), d("vix", 15.0), d("rf", 0.0), d("sprtrn", 0.0), fomc)
assert len(p) == 4 and p["fomc"].sum() == 1 and p["fomc_unscheduled"].sum() == 0
try:
    pb.merge_all(f.reset_index(), pd.concat([d("vix", 1.0), d("vix", 2.0)]), d("rf", 0.0), d("sprtrn", 0.0), fomc)
    raise SystemExit("duplicate not caught")
except ValueError:
    pass
same = pb.merge_all(f.reset_index(), pd.concat([d("vix", 1.0)] * 2), d("rf", 0.0), d("sprtrn", 0.0), fomc)
assert len(same) == 4
print("all checks passed")
