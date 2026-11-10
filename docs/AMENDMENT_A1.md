# Amendment A1 (post-freeze, 2026-11-10): development release times

`PRE_ANALYSIS_PLAN.md` and the frozen scripts (03-06, 08) are not edited. This amendment records a measurement error found after the holdout run.

Finding: eight 2011-2012 press-conference meetings released the statement at 12:20-12:35 ET (`data/raw/fomc_release_times_verified.csv`, Federal Reserve pages), not 14:15 ET, so the frozen 14:00 window end followed the announcement. Holdout statements (2020 onward) are released at 14:00 ET: unaffected. The VIX threshold 15.07 is unaffected (VIX only).

Corrected development benchmark (`code/12_dev_corrected.py`, dev only, 12:00 ET end for the eight): mean 2.8 bps (frozen run 6.2); 2010-14 2.9 vs 2015-19 2.8 (no decline); calm -6.6; anxious 12.6 (19.3); contrast 19.2 (26.0), wild p 0.057 (0.059); slope 1.87; matched placebo -11.9 bps (p=0.65); MDE 80% power: 21.8 bps all holdout, 40.3 bps anxious half (frozen plan: 27.4, 41.9).

Status: exploratory correction made after seeing the holdout; it changes the comparison benchmark only. Holdout outputs unchanged. Frozen-run numbers remain in `output/tables/T05_*`, `T06_*`.
