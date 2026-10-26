"""
Cross-check the futures grid against the SPY grid on development years only.

Compares 24 hour log returns to the 13:45 cutoff between consecutive common
trading days, skipping windows that span a futures contract roll. Run from the
repo root:  python code/02_crosscheck_es_spy.py
"""
import glob

import numpy as np
import pandas as pd


def load(pattern):
    d = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(pattern))])
    d["date"] = pd.to_datetime(d["date"])
    return d.drop_duplicates("date").set_index("date").sort_index()


spy = load("data/raw/spy_grid/dev/spy_grid_*.csv")
es = load("data/raw/es_grid/dev/es_grid_*.csv")
common = spy.index.intersection(es.index)
c = pd.DataFrame({"spy": spy.loc[common, "px_1345"], "es": es.loc[common, "px_1345"],
                  "iid": es.loc[common, "iid_1345"]}).dropna()
c = c[c.index >= "2010-06-07"]
r = np.log(c[["spy", "es"]]).diff()
r["same"] = c["iid"] == c["iid"].shift(1)
r = r[r["same"]].dropna()
gap = (r["es"] - r["spy"]) * 1e4

d = gap.index
quarterly = (d.dayofweek == 4) & (d.day >= 15) & (d.day <= 21) & d.month.isin([3, 6, 9, 12])
big = gap[gap.abs() > 25]
rest = gap[~quarterly]

print("common days %d, returns compared %d" % (len(c), len(r)))
print("correlation %.4f" % r["spy"].corr(r["es"]))
print("all days: mean %.2f bps, std %.2f bps" % (gap.mean(), gap.std()))
print("days over 25 bps: %d, of which third Friday of Mar/Jun/Sep/Dec: %d"
      % (len(big), int(np.isin(big.index, d[quarterly]).sum())))
print("mean gap on those quarterly days: %.1f bps (SPY goes ex-dividend)" % gap[quarterly].mean())
print("excluding quarterly days: std %.2f bps" % rest.std())
print("other outliers (likely bad SPY prints):")
print(big[~np.isin(big.index, d[quarterly])].round(1).to_string())
