"""
Pull daily series from WRDS: Fama-French risk-free rate, CRSP S&P 500 daily
return (cross-check only), and the VIX if WRDS carries it for your subscription.

Output goes to <out>/dev/ (before 2020) and <out>/holdout/ (2020 onward).

Usage:
    python 02_pull_daily_series.py --out daily_series

If the VIX table is not found the script says so. In that case download VIXCLS
from FRED (a free CSV) and place it in the same folder as vix_fred.csv.
"""

import argparse
from pathlib import Path

import pandas as pd

HOLDOUT_START = "2020-01-01"

QUERIES = {
    "ff_daily": "select date, mktrf, smb, hml, rf from ff.factors_daily where date >= '1993-01-01'",
    "crsp_sp500": "select date, sprtrn, vwretd from crsp.dsi where date >= '1993-01-01'",
    "cboe_vix": "select * from cboe.cboe where date >= '1993-01-01'",
}


def save(df, out, name):
    df["date"] = pd.to_datetime(df["date"])
    for sub, part in (("dev", df[df["date"] < HOLDOUT_START]),
                      ("holdout", df[df["date"] >= HOLDOUT_START])):
        d = Path(out) / sub
        d.mkdir(parents=True, exist_ok=True)
        part.to_csv(d / (name + ".csv"), index=False)
    print("%s: %d rows, %s to %s, columns %s"
          % (name, len(df), df["date"].min().date(), df["date"].max().date(), list(df.columns)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="daily_series")
    a = ap.parse_args()

    import wrds
    db = wrds.Connection()
    for name, sql in QUERIES.items():
        try:
            save(db.raw_sql(sql), a.out, name)
        except Exception as e:
            print("%s: not available (%s)" % (name, str(e)[:120]))
            if name == "cboe_vix":
                print("Use FRED series VIXCLS instead and save it as vix_fred.csv")


if __name__ == "__main__":
    main()
