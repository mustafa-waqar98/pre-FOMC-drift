# Pre-FOMC announcement drift after 2020

Does the pre-FOMC equity return drift survive after 2020, and is it concentrated in high-uncertainty (high-VIX) meetings? The specification, state threshold (VIX 15.07, the 2010-2019 median) and inference were frozen in `docs/PRE_ANALYSIS_PLAN.md` (tag `spec-frozen`) before the 2020-2026 holdout was run, once.

## Main results
- Holdout (52 scheduled meetings, 2020-2026): mean excess window return 38.3 bps; Fed-minus-matched-VIX placebo +55.5 bps (p = 0.002).
- Anxious-state premium 37.8 bps (year-clustered wild bootstrap p = 0.149); anxious-minus-calm contrast -2.6 bps (p = 0.946) against +19.2 bps in development. Power is limited: seven year clusters, nine calm meetings.
- Amendment A1 (post-freeze): eight 2011-2012 development meetings released at 12:20-12:35 ET, so the frozen window end followed the announcement. Corrected development mean is 2.8 bps (frozen run 6.2), with no post-2015 decline. The holdout is unaffected. See `docs/AMENDMENT_A1.md`.

- Exploratory (post-hoc, `code/13_pooled_exploratory.py`): holdout anxious-premium 95% CI [-10.6, 86.2] bps; pooling development and holdout (129 meetings, 17 years) gives a contrast of 13.2 bps (wild p = 0.163) and a VIX slope of 3.47 bps/pt (wild p = 0.075).

## Layout
`data/raw` (inputs, never edited; includes `fomc_release_times_verified.csv`), `data/processed`, `code` (numbered pipeline), `output` (tables, figures, raw run outputs), `paper` (LaTeX), `docs` (plan, amendment, referee review, data dictionary, run log).

## Reproduce
`pip install -r requirements.txt`, then `make all` (tests, development estimates, corrected benchmark, figures, paper). The holdout scripts `08_holdout.py` and `09_secondary.py` are run-once and are not in `make all`; their raw outputs are `output/T08_holdout_raw.txt` and `output/T09_secondary_raw.txt`. `code/10_report.py` builds figures and tables from saved outputs only. Data columns are described in `docs/DATA_DICTIONARY.md`.

## Status
All roadmap tasks are complete. Open limits are listed in `docs/REFEREE_REVIEW.md`: few clusters, thin calm cell, futures rather than the cash index, no intraday data before 2010, and the press-conference subsample excluding 2020 (run-once rule). Citations were verified against bibliographic records and, for Lucca-Moench and Martello, against primary text.
