# Data access findings

STATUS: APPROVED

## WRDS TAQ read access (checked 2026-10-25, first trading day of each year)

| Years | taqmsec (millisecond TAQ) |
|---|---|
| 2003-2008 | DENIED |
| 2009-2017 | ok |
| 2018-2026 | DENIED |

The old `taq` schema shows no tables for this account. Listing works for
2003-09-10 to 2026-10-07, so days are visible even where reads are denied.

## What this means

Intraday SPY prices from WRDS cover 2009 to 2017 only. The design needs
1994-2019 for the original premium and 2020-2026 for the holdout. Neither
main sample is available from this source. Daily close-to-close data cannot
test the window, which ends before the statement.

## Decision needed from the user

Source for intraday S&P 500 exposure (SPY or e-mini futures) for 1994-2008 and
2018-2026, or a redesign around what is available. Until this file says
STATUS: APPROVED

The grid format (last price at fixed Eastern clock times per day) is source
independent, so code written for T03 and T04 stays valid.

## Decision, 2026-10-25

Paid vendor declined. Intraday source is S&P e-mini futures 1-minute bars from
Databento (free account credit, estimated cost 20.91 USD for 5.7 million bars,
2010-06-06 to 2026-10-25). Files: `data/raw/es_grid/dev/` (2010-2019) and
`data/raw/es_grid/holdout/` (2020-2026). WRDS SPY 2009-2017 is the cross-check.
The sample starts mid-2010. Years before 2010 have no intraday source; earlier
evidence enters as published results, not as an estimate.

## ES grid sanity pass (development years only, 2010-2019)

- 2,963 rows, no duplicate dates, 2010-06-06 to 2019-12-31.
- 488 Sunday rows with no pre-cutoff bars. Drop rows with missing px_1345.
- 2,457 valid trading days. 75 are holidays or short days (no bars in the five
  minutes before the cutoff); the panel builder flags and drops them.
- Contract changes: exactly 4 per year, one per quarterly roll, 39 in total.
- Price range 1012 to 3242, consistent with the index over the period.
- All 77 scheduled FOMC meetings in the window have a row. 75 have a clean
  window; 2 fall in a roll window and are flagged for exclusion or for the
  second contract.
- Window end uses 14:00 ET before 2013-03-01 and 13:45 ET after, matching the
  calendar builder. Release times are still unverified per meeting.

## Still missing before the DATA gate can be approved
Daily risk-free rate and VIX history.

## Approval, 2026-10-25

Approved inputs (DATA gate satisfied):
- data/raw/es_grid/dev/ and data/raw/es_grid/holdout/ (ES 1-minute grid, 2010-06 to 2026-10)
- data/raw/daily_series/{dev,holdout}/ff_daily.csv, cboe_vix.csv, crsp_sp500.csv
- data/raw/fomc_meetings_raw.csv and data/processed/fomc_calendar.csv

Cleaning rules, fixed in advance:
- VIX: drop rows with a missing close; for duplicate dates keep the last row. The 2 duplicates
  (2003-09-22, 2003-10-30) share the same close; the 3 missing closes (1997-01-31, 1997-11-26,
  2003-08-24) all precede the sample. No effect on 2010 onward.
- Risk-free: Fama-French file ends 2026-08-31. Futures returns are treated as excess returns,
  so the rate is used only in the SPY cross-check.
- VIX is daily only. An intraday VIX change is not available; the communication versus
  arbitrage test needs a different source or a weaker version. Decide at T09.
- Holdout folders must not be opened before the FROZEN gate.

Not gating: WRDS SPY grid for 2009-2017 (cross-check of futures against SPY).

## Futures versus SPY cross-check (2010-2017, development years)

Script: code/02_crosscheck_es_spy.py. Output: output/tables/crosscheck_es_spy.txt.

- Correlation of 24 hour returns to the 13:45 cutoff: 0.9966 over 1,869 windows.
- Mean gap 0.63 bps. 31 of the 33 days with a gap above 25 bps are third Fridays of
  March, June, September and December, where SPY goes ex-dividend (mean gap 49.5 bps).
  Excluding those days the gap has a standard deviation of 3.2 bps.
- The other two (2012-05-25 and 2012-05-29) come from one bad SPY print at 13:45 on
  2012-05-25 (131.5355 against 132.49 and 132.415 either side). The futures are clean.
  SPY sale-condition filtering is not applied; that is why SPY stays a cross-check only.
- None of the large gaps fall on an FOMC date.
- Conclusion: the futures grid is validated against an independent source.
