"""Panel builder: one row per trading day, with logged row counts at every merge.

Inputs: ES grid CSVs, CBOE VIX, Ken French daily rf, CRSP S&P 500 return, FOMC calendar.
Holdout guard: dates after CUTOFF are dropped unless allow_holdout=True (FROZEN gate).
"""
import glob
import logging
import sys
from pathlib import Path

import pandas as pd

CUTOFF = pd.Timestamp("2019-12-31")
KEY = ["0945", "1200", "1330", "1345", "1400", "1415", "1430", "1545", "1600"]
log = logging.getLogger("panel")


def _n(step, df):
    log.info("%-28s rows=%d", step, len(df))
    return len(df)


def load_grid(paths, allow_holdout=False):
    df = pd.concat([pd.read_csv(p, dtype={"date": str}) for p in paths], ignore_index=True)
    df["date"] = pd.to_datetime(df["date"])
    _n("grid raw", df)
    if not allow_holdout:
        df = df[df["date"] <= CUTOFF]
        _n("grid after cutoff guard", df)
    dup = df["date"].duplicated().sum()
    if dup:
        raise ValueError(f"{dup} duplicate grid dates")
    return df.sort_values("date").reset_index(drop=True)


def flag_grid(df):
    """Drop days with no bars at all (weekends/holidays); flag half days and missing prints."""
    df = df.copy()
    px = [f"px_{k}" for k in KEY]
    nb = [f"nb5_{k}" for k in KEY]
    df = df[df[px].notna().any(axis=1)]
    _n("grid with any price", df)
    # half day: the 16:00 print is stale (last bar well before 15:55) or the 15:45 print is missing
    last = pd.to_datetime(df["tm_1600"], format="%H:%M", errors="coerce")
    df["half_day"] = ((last.dt.hour * 60 + last.dt.minute) < 15 * 60 + 55).fillna(True).astype(int)
    df["missing_trade"] = (df[nb].fillna(0).eq(0).any(axis=1) | df[px].isna().any(axis=1)).astype(int)
    df["roll_window"] = (df[[f"iid_{k}" for k in KEY]].nunique(axis=1) > 1).astype(int)
    return df


def merge_all(grid, vix, rf, sp, fomc):
    p = grid.copy()
    n0 = _n("panel base", p)
    for name, d, cols in [("vix", vix, ["vix"]), ("rf", rf, ["rf"]), ("sp500", sp, ["sprtrn"])]:
        d = d.copy()
        d["date"] = pd.to_datetime(d["date"])
        dups = d[d["date"].duplicated(keep=False)]
        if len(dups) and (dups.groupby("date")[cols[0]].nunique() == 1).all():
            log.info("%s: %d duplicate dates with identical %s, kept first", name, dups["date"].nunique(), cols[0])
            d = d.drop_duplicates("date", keep="first")
        if d["date"].duplicated().any():
            raise ValueError(f"duplicate dates in {name}")
        p = p.merge(d[["date"] + cols], on="date", how="left", validate="one_to_one")
        if len(p) != n0:
            raise ValueError(f"merge {name} changed row count")
        miss = int(p[cols[0]].isna().sum())
        log.info("merge %-22s rows=%d missing=%d", name, len(p), miss)
    p["cash_closed"] = (p["vix"].isna() & p["sprtrn"].isna()).astype(int)
    p["valid"] = ((p["half_day"] == 0) & (p["missing_trade"] == 0) & (p["cash_closed"] == 0) & p["rf"].notna()).astype(int)
    log.info("valid days=%d cash_closed=%d", p["valid"].sum(), p["cash_closed"].sum())
    f = fomc.copy()
    f["date"] = pd.to_datetime(f["decision_date"])
    sched = set(f.loc[f["meeting_type"] == "scheduled", "date"])
    unsch = set(f.loc[f["meeting_type"] != "scheduled", "date"])
    p["fomc"] = p["date"].isin(sched).astype(int)
    p["fomc_unscheduled"] = p["date"].isin(unsch).astype(int)
    lost = sorted(d for d in sched if d not in set(p["date"]) and grid["date"].min() <= d <= grid["date"].max())
    log.info("scheduled FOMC dates in range but absent from panel: %d %s", len(lost), [str(d.date()) for d in lost])
    _n("panel final", p)
    return p


def build(root=".", allow_holdout=False):
    r = Path(root) / "data" / "raw"
    sub = ["dev"] + (["holdout"] if allow_holdout else [])
    grid = load_grid(sorted(g for s in sub for g in glob.glob(str(r / "es_grid" / s / "*.csv"))), allow_holdout)
    cat = lambda n: pd.concat([pd.read_csv(f) for s in sub for f in [r / "daily_series" / s / n]])
    p = merge_all(flag_grid(grid), cat("cboe_vix.csv"), cat("ff_daily.csv"), cat("crsp_sp500.csv"),
                  pd.read_csv(r / "fomc_meetings_raw.csv"))
    if not allow_holdout:
        assert p["date"].max() <= CUTOFF
    return p


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stdout)
    out = build(".")
    Path("output").mkdir(exist_ok=True)
    out.to_csv("output/panel_dev.csv", index=False)
    print(out[["half_day", "missing_trade", "roll_window", "fomc"]].sum().to_dict())
