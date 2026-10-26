run_date | task | outcome | blockers
2026-10-25 | T01 | WRDS scripts written, SQL logic tested on synthetic data in DuckDB, not yet run against WRDS | needs user: run --probe on WRDS and return output
2026-10-25 | T01 fix | first probe on WRDS failed in list_days (percent sign in query); fixed, test added | needs user: re-upload 01_pull_spy_grid.py and rerun --probe
2026-10-25 | T01 probe | day listing works (5806 days, 2003-09-10 to 2026-10-07); taqm_2018 permission denied; old pre-2003 TAQ not found under ctm name | needs user: run 00_access_check.py on WRDS and paste output
2026-10-25 | access check | WRDS TAQ ms readable 2009-2017 only; 2003-2008 and 2018-2026 denied; old taq empty | DATA gate now requires STATUS APPROVED in docs/DATA_ACCESS.md
2026-10-25 | data route | user declined paid vendor; Databento free credit route scripted (cost estimate first), grid logic tested on synthetic bars | needs user: run --estimate on own computer, paste output
