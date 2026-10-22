"""
Build the analysis FOMC calendar from the raw date list.

Input:  data/raw/fomc_meetings_raw.csv
Output: data/processed/fomc_calendar.csv

Adds regime flags and the window cutoff timestamp. Run once:
    python code/00_build_calendar.py
"""

import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "fomc_meetings_raw.csv"
OUT = ROOT / "data" / "processed" / "fomc_calendar.csv"

# Sample starts at the first meeting whose outcome was announced the same day
# regardless of whether policy changed (1994-09-27). Earlier 1994 meetings
# announced only changes, so a no-change meeting had no scheduled release.
SAMPLE_START = pd.Timestamp("1994-09-27")

# Press conferences: none before 2011-04-27; from 2011-04-27 to 2018 they
# followed SEP meetings only; from 2019-01-30 they follow every meeting.
# Source: Federal Reserve FEDS Note, 2021-10-12.
PRESSER_START = pd.Timestamp("2011-04-27")
PRESSER_EVERY_MEETING = pd.Timestamp("2019-01-30")

# Statement release time. 14:15 ET through the February 2013 meeting, 14:00 ET
# from the March 2013 meeting on. VERIFY per meeting before the window is
# built: early-sample release times varied. See docs/DESIGN_NOTES.md.
RELEASE_TIME_CHANGE = pd.Timestamp("2013-03-01")

# Window closes this many minutes before the scheduled release.
BUFFER_MIN = 15

PERIODS = [
    ("P1_in_sample", "1994-09-27", "2011-03-31"),
    ("P2_working_paper", "2011-04-01", "2015-01-31"),
    ("P3_published", "2015-02-01", "2019-12-31"),
    ("P4_holdout", "2020-01-01", "2026-09-30"),
]


def assign_period(d):
    for name, lo, hi in PERIODS:
        if pd.Timestamp(lo) <= d <= pd.Timestamp(hi):
            return name
    return "outside_sample"


def main():
    raw = pd.read_csv(RAW, parse_dates=["decision_date"])

    n_raw = len(raw)
    assert raw["decision_date"].is_unique, "duplicate decision dates in raw file"

    df = raw[raw["meeting_type"] == "scheduled"].copy()
    n_scheduled = len(df)

    df = df[df["decision_date"] >= SAMPLE_START].copy()
    df = df.sort_values("decision_date").reset_index(drop=True)

    df["release_time"] = df["decision_date"].apply(
        lambda d: "14:00" if d >= RELEASE_TIME_CHANGE else "14:15"
    )
    df["release_ts"] = pd.to_datetime(
        df["decision_date"].dt.strftime("%Y-%m-%d") + " " + df["release_time"]
    )
    df["window_close_ts"] = df["release_ts"] - pd.Timedelta(minutes=BUFFER_MIN)
    df["release_time_verified"] = 0

    def presser(d):
        if d < PRESSER_START:
            return 0
        if d >= PRESSER_EVERY_MEETING:
            return 1
        return pd.NA  # SEP meetings only; needs per-meeting verification

    df["press_conference"] = df["decision_date"].apply(presser).astype("Int64")
    df["period"] = df["decision_date"].apply(assign_period)

    cols = [
        "decision_date", "period", "release_time", "window_close_ts",
        "release_time_verified", "press_conference", "source_page", "note",
    ]
    df[cols].to_csv(OUT, index=False)

    print(f"raw rows                  {n_raw}")
    print(f"scheduled meetings        {n_scheduled}")
    print(f"unscheduled excluded      {n_raw - n_scheduled}")
    print(f"in sample from {SAMPLE_START.date()}  {len(df)}")
    print()
    print(df.groupby("period", sort=False).size().to_string())
    print()
    print("press_conference flag")
    print(df["press_conference"].value_counts(dropna=False).to_string())
    print()
    print(f"written: {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
