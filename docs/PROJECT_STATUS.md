# Status

Updated 2026-10-21.

## Done
- Repo layout and git history.
- FOMC meeting dates 1994-2026 collected from Federal Reserve primary pages,
  308 rows, scheduled and unscheduled flagged: `data/raw/fomc_meetings_raw.csv`.
- Analysis calendar derived with regime flags: `data/processed/fomc_calendar.csv`.
  258 scheduled meetings from 1994-09-27, of which 53 in the 2020-2026 holdout.
- Press conference regime rule confirmed from the Fed's FEDS note of 2021-10-12.
- Open design issues recorded in `docs/DESIGN_NOTES.md`.

## Blocked on data
Nothing further can run until the price, volatility and risk-free series arrive.
The intraday prices are the binding input: daily close-to-close returns measure
a different quantity and cannot test the pre-announcement window.

## Next, in order
1. Write the WRDS extraction script for intraday prices, to be run on the WRDS
   server so only a small daily-level file comes back.
2. Build the daily panel and log merge counts.
3. Reproduce the pre-2020 result, including the post-2015 decline.
4. Recalibrate power with realized volatility.
5. Freeze `docs/PRE_ANALYSIS_PLAN.md`, record the code hash, then run the
   holdout once.
6. Draft the paper, verifying each citation against the primary source.

## Holdout discipline
No estimate on data after 2019-12-31 has been run.
