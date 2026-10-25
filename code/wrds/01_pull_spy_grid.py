"""
Pull a daily grid of SPY prices from TAQ. Run this on the WRDS server.

For every trading day it records the last SPY trade at or before each clock
time in GRID (Eastern time), the timestamp of that trade, and the number of
trades in the five minutes before it. Returns for any window are built later
from this grid, so the TAQ query is run only once.

Output is one row per trading day, split into two folders so that development
code can never read holdout years by accident:
    <out>/dev/      years before 2020
    <out>/holdout/  2020 onward

Usage:
    python 01_pull_spy_grid.py --probe            check schema on one day, then stop
    python 01_pull_spy_grid.py --dry-run          print the SQL, no connection
    python 01_pull_spy_grid.py --out spy_grid     full run, resumable
    python 01_pull_spy_grid.py --out spy_grid --source taq --start 2003-01-01 --end 2014-12-31 --sample 100
                                                  cross-check run on the old second-level TAQ

The column names in TAQ differ between the old and new tables. They are looked
up from the database at run time. Nothing here has been run against WRDS yet;
use --probe first and read what it prints.
"""

import argparse
import random
import re
import sys
import time
from pathlib import Path

import pandas as pd

GRID = ["09:45", "12:00", "13:30", "13:45", "14:00", "14:15", "14:30", "15:45", "16:00"]
HOLDOUT_START_YEAR = 2020
DEFAULT_START = "1994-08-01"
PROBE_DAY = "2018-06-13"  # a development-period FOMC day

SCHEMAS = ["taqmsec", "taq"]  # millisecond TAQ first, second-level TAQ as fallback

# logical name -> candidate column names, first match wins
CANDIDATES = {
    "time": ["time_m", "time"],
    "price": ["price"],
    "size": ["size"],
    "corr": ["tr_corr", "corr"],
    "root": ["sym_root", "symbol"],
    "suffix": ["sym_suffix"],
    "seq": ["tr_seqnum"],
}
REQUIRED = ["time", "price", "size", "corr", "root"]

DEFAULT_MAP = {
    "time": "time_m", "price": "price", "size": "size", "corr": "tr_corr",
    "root": "sym_root", "suffix": "sym_suffix", "seq": "tr_seqnum",
}


def build_sql(schema, table, m):
    values = ", ".join("(time '%s')" % g for g in GRID)
    suffix = "and %s is null" % m["suffix"] if m.get("suffix") else ""
    seq = ", %s desc" % m["seq"] if m.get("seq") else ""
    seq_col = ", %s as sq" % m["seq"] if m.get("seq") else ", 0 as sq"
    order_seq = ", t.sq desc" if m.get("seq") else ""
    return f"""
with g(gt) as (values {values}),
t as (
  select {m['time']} as tm, {m['price']} as px, {m['size']} as sz{seq_col}
  from {schema}.{table}
  where {m['root']} = 'SPY' {suffix}
    and cast({m['corr']} as text) in ('0', '00')
    and {m['price']} > 0 and {m['size']} > 0
    and {m['time']} >= time '09:30' and {m['time']} <= time '16:00'
)
select g.gt::text as gt,
       l.tm::text as last_tm,
       l.px as last_px,
       (select count(*) from t where t.tm > g.gt - interval '5 minutes' and t.tm <= g.gt) as n5,
       s.first_tm::text as first_tm_day,
       s.last_tm_day::text as last_tm_day,
       s.n_day as n_day,
       s.vol_day as vol_day
from g
left join lateral (
  select tm, px from t where t.tm <= g.gt order by t.tm desc{order_seq} limit 1
) l on true
cross join (
  select min(tm) as first_tm, max(tm) as last_tm_day, count(*) as n_day, sum(sz) as vol_day from t
) s
order by g.gt
"""


def days_sql(schema):
    # No percent sign allowed in any query: the WRDS driver reads a bare one
    # as a parameter marker and fails with "immutabledict is not a sequence".
    return ("select table_name from information_schema.tables "
            "where table_schema = '%s' and table_name ~ '^ctm_[0-9]{8}$'" % schema)


def list_days(db, schema):
    names = db.raw_sql(days_sql(schema))["table_name"].tolist()
    days = {}
    for n in names:
        mo = re.fullmatch(r"ctm_(\d{4})(\d{2})(\d{2})", n)
        if mo:
            days["%s-%s-%s" % mo.groups()] = n
    return days


def resolve_columns(db, schema, table):
    sql = ("select column_name from information_schema.columns "
           "where table_schema = '%s' and table_name = '%s'" % (schema, table))
    have = set(db.raw_sql(sql)["column_name"].str.lower())
    m = {}
    for key, options in CANDIDATES.items():
        hit = [o for o in options if o in have]
        if hit:
            m[key] = hit[0]
    missing = [k for k in REQUIRED if k not in m]
    if missing:
        raise RuntimeError("columns not found in %s.%s for %s. Columns present: %s"
                           % (schema, table, missing, sorted(have)))
    return m


def query_day(db, schema, table, m):
    for attempt in (1, 2):
        try:
            return db.raw_sql(build_sql(schema, table, m))
        except Exception as e:  # one retry, then give up on this day
            if attempt == 2:
                print("FAILED %s.%s: %s" % (schema, table, str(e)[:200]), file=sys.stderr)
                return None
            time.sleep(5)


def to_row(day, source, df):
    row = {"date": day, "source": source}
    for _, r in df.iterrows():
        tag = r["gt"][:5].replace(":", "")
        row["px_" + tag] = r["last_px"]
        row["tm_" + tag] = r["last_tm"]
        row["n5_" + tag] = r["n5"]
    first = df.iloc[0]
    row["first_tm_day"] = first["first_tm_day"]
    row["last_tm_day"] = first["last_tm_day"]
    row["n_day"] = first["n_day"]
    row["vol_day"] = first["vol_day"]
    return row


def out_path(out, source_tag, year):
    sub = "holdout" if year >= HOLDOUT_START_YEAR else "dev"
    d = Path(out) / sub
    d.mkdir(parents=True, exist_ok=True)
    return d / ("spy_grid_%s_%d.csv" % (source_tag, year))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="spy_grid")
    ap.add_argument("--start", default=DEFAULT_START)
    ap.add_argument("--end", default=time.strftime("%Y-%m-%d"))
    ap.add_argument("--source", choices=["auto", "taq", "taqmsec"], default="auto")
    ap.add_argument("--sample", type=int, default=0, help="random sample of N days, for cross-checks")
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    if a.dry_run:
        print(build_sql("taqmsec", "ctm_%s" % PROBE_DAY.replace("-", ""), DEFAULT_MAP))
        return

    import wrds
    db = wrds.Connection()

    schemas = SCHEMAS if a.source == "auto" else [a.source]
    day_map = {}
    for s in reversed(schemas):  # earlier entries in SCHEMAS win
        for d, t in list_days(db, s).items():
            day_map[d] = (s, t)
    print("trading days found: %d, from %s to %s"
          % (len(day_map), min(day_map), max(day_map)))

    if a.probe:
        s, t = day_map[PROBE_DAY]
        m = resolve_columns(db, s, t)
        print("probe table:", s, t)
        print("column map:", m)
        df = query_day(db, s, t, m)
        print(df.to_string())
        return

    days = sorted(d for d in day_map if a.start <= d <= a.end)
    if a.sample:
        random.seed(1)
        days = sorted(random.sample(days, min(a.sample, len(days))))
    print("days to pull: %d" % len(days))

    colmaps = {}
    rows_by_year = {}
    tag = a.source if a.source != "auto" else "auto"
    done = 0
    for d in days:
        s, t = day_map[d]
        year = int(d[:4])
        path = out_path(a.out, tag, year)
        if year not in rows_by_year:
            if path.exists():
                rows_by_year[year] = pd.read_csv(path).to_dict("records")
            else:
                rows_by_year[year] = []
        if any(r["date"] == d for r in rows_by_year[year]):
            continue
        if s not in colmaps:
            colmaps[s] = resolve_columns(db, s, t)
        df = query_day(db, s, t, colmaps[s])
        if df is None or df.empty:
            continue
        rows_by_year[year].append(to_row(d, s, df))
        done += 1
        if done % 50 == 0:
            pd.DataFrame(rows_by_year[year]).to_csv(path, index=False)
            print("%s  pulled %d" % (d, done), flush=True)

    for year, rows in rows_by_year.items():
        if rows:
            pd.DataFrame(rows).sort_values("date").to_csv(out_path(a.out, tag, year), index=False)
    print("finished, %d new days" % done)


if __name__ == "__main__":
    main()
