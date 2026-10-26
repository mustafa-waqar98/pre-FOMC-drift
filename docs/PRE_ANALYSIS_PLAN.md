# Pre-analysis plan (DRAFT v1, not frozen)

Status: draft. Becomes binding only when committed as final with tag `spec-frozen` (task T07). Until then no estimate on data after 2019-12-31 may be run.

## Question
Does the pre-FOMC equity return drift reappear in high-uncertainty meetings after 2020, with publication and press-conference regime held fixed?

## Sample
- Development: scheduled FOMC meetings 1994-09-27 to 2019-12-31 (calendar in `data/processed/fomc_calendar.csv`).
- Holdout: scheduled meetings 2020-01-01 to 2026 (53 meetings). Read once, after freeze.
- Unscheduled meetings excluded from the main test.

## Outcome
Pre-announcement window return on the intraday grid, from the end of the prior trading session reference point to a 15 minute buffer before the statement release, in excess of the risk-free rate (daily file). Window and release-time rule as in `docs/DESIGN_NOTES.md`; release times to be merged from primary sources before freeze (UNVERIFIED).

## State variable
Lagged VIX measured one week before the meeting (primary definition). Anxious versus calm split at a threshold fixed on development data only; continuous VIX specification reported alongside.

## Specification (to be fixed at T07)
r_m = a + b*Anxious_m + controls + e_m, with the premium in anxious meetings tested as a + b. Alternative: r_m = a + c*VIX_m + e_m.

## Inference
- Episode-clustered standard errors (volatility episodes, not days).
- Wild cluster bootstrap and a permutation placebo on matched-VIX non-Fed days.
- Power simulated with episode clustering; report minimum detectable effect and state that a half-sized premium is not distinguishable from zero if that holds.

## Hypotheses
H1: premium positive in anxious holdout meetings. H2: premium smaller than the pre-2015 estimate. Magnitudes to be filled from development results (T05, T06), not from the literature (attribution UNVERIFIED).

## Open items before freeze
Decay clock (publication date convention); press-conference flag for 2011-2018 SEP meetings; release_time_verified; code hash.
