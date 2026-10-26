# Data access findings

STATUS: PENDING DECISION

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
