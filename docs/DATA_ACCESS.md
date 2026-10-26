# Data access findings

STATUS: PENDING (waiting on risk-free and VIX files)

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
STATUS: APPROVED with a list of files, the DATA gate is not satisfied.

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
