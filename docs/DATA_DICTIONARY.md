# Data dictionary

## Inputs (data/raw, never edited)
- `es_grid/{dev,holdout}/es_grid_YYYY.csv`: S&P e-mini futures, last trade at fixed Eastern clock times per day. Per time HHMM in {0945,1200,1330,1345,1400,1415,1430,1545,1600}: `px_` price, `tm_` timestamp of that trade, `iid_` contract id, `nb5_` bars in the last five minutes.
- `spy_grid/dev`: SPY cross-check grid, same layout (2010-2017 dev days only).
- `daily_series/{dev,holdout}/cboe_vix.csv` (VIX close), `ff_daily.csv` (daily risk-free rate, percent), `crsp_sp500.csv` (S&P 500 return `sprtrn`).
- `fomc_meetings_raw.csv`, `fomc_meetings_2021_2026.csv`: meeting dates, `sep_meeting` (projections meeting), `press_conference`, `source_note`.

## Panel (code/03_build_panel.py), one row per trading day
`date`, `source`, price/time/contract/bar-count columns above, `half_day`, `missing_trade`, `roll_window` (futures roll), `vix`, `rf`, `sprtrn`, `cash_closed` (no cash session), `valid` (usable day), `fomc` (scheduled meeting day), `fomc_unscheduled`.

## Derived
- `r`: ln(P_end / P_1600 of previous valid day) minus `rf`; bps = r x 1e4. P_end = 13:45 print (14:00 release, from 2013-03-01 and holdout) or 14:00 print (earlier). Eight 2011-2012 meetings released at about 12:30 ET; see paper appendix, sensitivity.
- `vix_lag`: VIX five trading days before the meeting. `anx` = 1 if `vix_lag` > 15.07 (development median).
- `yr`: calendar year, the cluster id.
## Outputs
`output/T08_holdout_raw.txt`, `output/T09_secondary_raw.txt` (raw, run once), `output/tables/*.csv|txt`, `output/figures/*.pdf`.
