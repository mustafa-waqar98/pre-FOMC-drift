"""
Build a daily price grid from S&P e-mini futures 1-minute bars (Databento).
Run this on your own computer, not on WRDS.

    export DATABENTO_API_KEY=your_key      never put the key in the repo
    python 01_es_grid.py --estimate        prints the cost, downloads nothing
    python 01_es_grid.py --download        downloads year by year and builds the grid

The grid has the same layout as the WRDS SPY grid: for each trading day, the
last bar at or before each Eastern clock time in GRID. A 1-minute bar stamped
10:44 covers 10:44 to 10:45, so for a grid time T only bars stamped up to T minus
one minute count, and the price is that bar's close.

Columns per grid time HHMM: px_ close, tm_ stamp of that bar, nb5_ number of bars
in the five minutes before, iid_ contract id. If iid_ differs between two days
the window spans a contract roll and the panel builder drops it.

Output goes to <out>/dev (before 2020) and <out>/holdout (2020 onward).
Raw downloads are kept in <out>/raw so a changed grid never costs credit again.
"""

import argparse
import os
import sys
from pathlib import Path

import pandas as pd

GRID = ["09:45", "12:00", "13:30", "13:45", "14:00", "14:15", "14:30", "15:45", "16:00"]
DATASET = "GLBX.MDP3"
SYMBOL = "ES.v.0"        # front contract by volume
STYPE = "continuous"
SCHEMA = "ohlcv-1m"
WANT_START = "2010-06-01"
HOLDOUT_START_YEAR = 2020


def build_grid(df):
    """df: minute bars with a tz-aware index and columns close, instrument_id."""
    df = df.copy()
    df.index = df.index.tz_convert("America/New_York")
    df = df.sort_index()
    df["d"] = df.index.strftime("%Y-%m-%d")
    df["mins"] = df.index.hour * 60 + df.index.minute
    df["stamp"] = df.index.strftime("%H:%M")
    out = pd.DataFrame(index=sorted(df["d"].unique()))
    for g in GRID:
        h, m = int(g[:2]), int(g[3:])
        t = h * 60 + m
        tag = g.replace(":", "")
        before = df[df["mins"] <= t - 1]
        last = before.groupby("d").tail(1).set_index("d")
        out["px_" + tag] = last["close"]
        out["tm_" + tag] = last["stamp"]
        out["iid_" + tag] = last["instrument_id"]
        recent = before[before["mins"] >= t - 5]
        out["nb5_" + tag] = recent.groupby("d").size()
        out["nb5_" + tag] = out["nb5_" + tag].fillna(0).astype(int)
    out.index.name = "date"
    out.insert(0, "source", "databento_es")
    return out.reset_index()


def client():
    import databento as db
    key = os.environ.get("DATABENTO_API_KEY")
    if not key:
        sys.exit("set DATABENTO_API_KEY first")
    return db.Historical(key)


def date_range(c):
    r = c.metadata.get_dataset_range(dataset=DATASET)
    first = str(r["start"])[:10]
    last = str(r["end"])[:10]
    return max(first, WANT_START), last


def estimate(c):
    start, end = date_range(c)
    kw = dict(dataset=DATASET, symbols=[SYMBOL], stype_in=STYPE, schema=SCHEMA,
              start=start, end=end)
    print("range requested:", start, "to", end)
    print("records:", c.metadata.get_record_count(**kw))
    print("size in bytes:", c.metadata.get_billable_size(**kw))
    print("cost in USD:", c.metadata.get_cost(**kw))


def download(c, out):
    start, end = date_range(c)
    out = Path(out)
    (out / "raw").mkdir(parents=True, exist_ok=True)
    for year in range(int(start[:4]), int(end[:4]) + 1):
        s = max(start, "%d-01-01" % year)
        e = min(end, "%d-01-01" % (year + 1))
        if s >= e:
            continue
        sub = "holdout" if year >= HOLDOUT_START_YEAR else "dev"
        dest = out / sub / ("es_grid_%d.csv" % year)
        if dest.exists():
            print(year, "already done")
            continue
        raw = out / "raw" / ("es_%d.dbn.zst" % year)
        print(year, "downloading", s, "to", e, flush=True)
        store = c.timeseries.get_range(dataset=DATASET, symbols=[SYMBOL], stype_in=STYPE,
                                       schema=SCHEMA, start=s, end=e, path=str(raw))
        grid = build_grid(store.to_df())
        dest.parent.mkdir(parents=True, exist_ok=True)
        grid.to_csv(dest, index=False)
        print(year, "rows", len(grid), flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--estimate", action="store_true")
    ap.add_argument("--download", action="store_true")
    ap.add_argument("--out", default="es_grid")
    a = ap.parse_args()
    if a.estimate:
        estimate(client())
    elif a.download:
        download(client(), a.out)
    else:
        sys.exit("choose --estimate or --download")
