run_date | task | outcome | blockers
2026-10-25 | T01 | WRDS scripts written, SQL logic tested on synthetic data in DuckDB, not yet run against WRDS | needs user: run --probe on WRDS and return output
2026-10-25 | T01 fix | first probe on WRDS failed in list_days (percent sign in query); fixed, test added | needs user: re-upload 01_pull_spy_grid.py and rerun --probe
2026-10-25 | T01 probe | day listing works (5806 days, 2003-09-10 to 2026-10-07); taqm_2018 permission denied; old pre-2003 TAQ not found under ctm name | needs user: run 00_access_check.py on WRDS and paste output
2026-10-25 | access check | WRDS TAQ ms readable 2009-2017 only; 2003-2008 and 2018-2026 denied; old taq empty | DATA gate now requires STATUS APPROVED in docs/DATA_ACCESS.md
2026-10-25 | data route | user declined paid vendor; Databento free credit route scripted (cost estimate first), grid logic tested on synthetic bars | needs user: run --estimate on own computer, paste output
2026-10-25 | ES grid received | dev sanity pass clean: 2457 valid days, 4 rolls per year, all 77 dev FOMC dates present (2 in roll windows); holdout not opened | needs user: run 02_pull_daily_series.py on WRDS for rf and VIX
2026-10-25 | data gate | VIX and rf received and checked on dev years; DATA gate APPROVED | nothing blocking T02-T07; holdout untouched
2026-10-25 | cross-check | ES vs SPY validated on 2010-2017 dev days: corr 0.9966, gaps explained by SPY ex-dividend Fridays and one bad SPY print | nothing blocking
2026-10-26 | T02 | paper skeleton, UNVERIFIED bib, draft pre-analysis plan v1 (not frozen) added | none
2026-10-27 | T03 | code/03_build_panel.py + tests/test_panel.py: panel (2457 dev days, merges logged, flags half_day/missing_trade/cash_closed/valid; holdout guard); synthetic tests pass; 53 US-holiday ES days have no cash data (flagged), 2 duplicate VIX dates in 2003 identical close | none
