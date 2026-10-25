# WRDS extraction

Two scripts, run on the WRDS server so that only small daily files leave it.

## Steps

1. Log in to WRDS Cloud (or open a WRDS Jupyter terminal) and copy `code/wrds/` there.
2. Check the schema first. This pulls one development-period day and prints the
   column mapping and the result:

       python 01_pull_spy_grid.py --probe

   Paste the output back to Claude before running anything else. The column
   names in the old and new TAQ tables differ and have not been checked against
   WRDS yet.
3. Full run, resumable, in the background:

       nohup python 01_pull_spy_grid.py --out spy_grid > pull.log 2>&1 &

   Expect it to take hours. It can be stopped and restarted; finished days are skipped.
4. Daily series:

       python 02_pull_daily_series.py --out daily_series

5. Cross-check of the two TAQ generations over 2003 to 2014 (100 random days each):

       python 01_pull_spy_grid.py --out spy_grid_x --source taq --start 2003-01-01 --end 2014-12-31 --sample 100
       python 01_pull_spy_grid.py --out spy_grid_x --source taqmsec --start 2003-01-01 --end 2014-12-31 --sample 100

6. Copy `spy_grid/`, `daily_series/` and `spy_grid_x/` into `data/raw/` in the repo and push.

## Output

One row per trading day. Columns: `date`, `source`, then for each grid time
(0945, 1200, 1330, 1345, 1400, 1415, 1430, 1545, 1600): `px_` last trade price,
`tm_` timestamp of that trade, `n5_` trades in the five minutes before. Plus
`first_tm_day`, `last_tm_day`, `n_day`, `vol_day`. Times are Eastern.

A day with `last_tm_day` before 15:00 is a half day. A grid time with a low
`n5_` or an old `tm_` has a stale price and is flagged in the panel audit.

## Holdout separation

Years from 2020 are written to a `holdout/` folder. Development code reads only
`dev/`. The holdout folder is not opened until the specification is frozen.

## Known limits

- Sale-condition filters are not applied beyond the correction flag. Out-of-sequence
  trades could matter at the window edges; the audit flags stale prices instead.
- Column names are looked up at run time and are UNVERIFIED until the probe is run.
- The VIX change test needs an intraday VIX. WRDS does not carry one as far as I
  know; this is UNVERIFIED. The fallback is a close-to-close VIX change, which does
  not match the price window.

## Licensing

TAQ is licensed. The derived grid is small, but keep this repository private while
it holds data. Before making it public, remove `data/raw/spy_grid*` and keep only
these scripts.
