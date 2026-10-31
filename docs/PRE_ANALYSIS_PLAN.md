# Pre-analysis plan (FINAL, frozen at tag `spec-frozen`)

Binding once committed with tag `spec-frozen`. The holdout (T08) is run once, after this tag, with the code listed below. Any later deviation is reported as a deviation.

## Question
Does a pre-FOMC equity return premium appear in high-uncertainty meetings after 2020, with the communication regime held fixed?

## Data
- Intraday source: S&P e-mini futures 1-minute bars (Databento), last price at fixed Eastern clock times. WRDS SPY 2009-2017 is a cross-check only.
- VIX and risk-free rate: daily files in `data/raw/daily_series/`.
- Development sample: scheduled FOMC meetings 2010-06 to 2019-12-31 (77 usable meetings). Holdout: scheduled meetings 2020-01-01 onward (calendar `data/raw/fomc_meetings_2021_2026.csv` and `data/raw/fomc_meetings_raw.csv`). Unscheduled meetings excluded.
- Years before 2010 have no intraday source and enter only as published results, not estimates.
- A meeting is usable if the meeting day and the prior session are both valid (no half-day, missing-trade or cash-closed flag) and the outcome and lagged VIX are non-missing.

## Outcome
r_m = ln(P_end / P_prevclose) - rf, in basis points, where P_prevclose is the 16:00 ET print of the previous valid session and P_end is the 13:45 ET print. This is the 15 minute buffer before a 14:00 ET statement. The rule is 14:00 ET release (13:45 end) from 2013-03-01 and 14:15 ET release (14:00 end) before. In the 2020-onward sample every meeting uses the 13:45 end. Release times are a rule, not per-meeting observations: `release_time_verified` = 0 for all rows (UNVERIFIED).

## State variable
VIX close five trading days before the meeting date (lagged one week). Anxious = lagged VIX above the development-sample median, fixed at **15.07** VIX points (39 calm, 38 anxious in development). The threshold is not re-estimated on the holdout.

## Specification
Primary: r_m = a + b * Anxious_m + e_m. Premium in calm meetings is a; in anxious meetings a + b. The primary test statistic is the anxious-meeting premium a + b with H1: a + b > 0.
Secondary (reported alongside, not substituted): r_m = a + c * VIX_m + e_m with VIX_m the lagged VIX in points.
No controls in the primary specification. The sign and size of b and c are reported whatever they are.

## Inference
- Cluster by calendar year (provisional episode proxy fixed ex ante). CR1 cluster-robust standard errors.
- Wild cluster bootstrap-t, 999 draws, seed 1, for b = 0 and for a + b = 0.
- Permutation placebo against non-FOMC days matched on lagged VIX (2000 draws, seed 2), reported overall and by regime.
- Because the holdout has about seven year-clusters, bootstrap p-values are primary and asymptotic t statistics are descriptive.

## Hypotheses and benchmarks (from development data only)
Development (2010-2019, bps): all meetings 6.2 (t=0.89); calm -6.6; anxious 19.3 (t=1.69); anxious minus calm 26.0 (t=2.24, wild bootstrap p=0.059); continuous VIX slope 1.60 bps per VIX point (t=1.65); matched-VIX placebo Fed minus non-Fed -8.6 bps (p=0.90); 2010-14 9.8 vs 2015-19 2.8 bps (decline not significant).
- H1: anxious-meeting premium a + b > 0 in the holdout.
- H2: the holdout anxious premium is smaller than the development anxious estimate of 19.3 bps.
- H3: b > 0 (anxious minus calm difference positive).
Literature magnitudes are not used to scale hypotheses (attribution UNVERIFIED).

## Power statement
From development realized volatility (meeting sd 50.8 bps; anxious 63.5; calm 30.1; year ICC 0.07), the 80% power minimum detectable effect is 27.4 bps for all holdout meetings and 41.9 bps for the anxious half (19.9 bps if the anxious sd equals the calm sd). A premium near the development estimate of 19.3 bps is therefore not reliably detectable in the anxious half. The holdout is reported as a bound on the premium, with a confidence interval, not as a sharp test of a point value. Null results are not interpreted as absence of a premium.

## Exclusions and deviations
- Not part of the frozen test: VIX-change test, press-conference subsample, robustness table (T09). They are labelled exploratory-secondary and cannot change the primary conclusion.
- Press-conference flag for 2011-2018 SEP meetings is incomplete; only the T09 subsample uses it.
- Decay clock (publication date convention) is not used in the primary test.

## Code
Frozen estimation code and SHA-256 of each file:

| File | SHA-256 |
|---|---|
| code/03_build_panel.py | a9e8e1414688c6cb3357e23222b839d5df0c02ea5c7d78f16e8e9cab8948e1bc |
| code/04_estimation.py | 471f24bfee895a036ae29ecad73c9619534f150437c32bbc941ddf961cb3a80b |
| code/05_dev_premium.py | 2be296ec28a5a0b51ef04c8b26054b69005f2ec160908fe8e76863c08098b71a |
| code/06_dev_calm_anxious.py | f3ec1d22e81609b485128b8c04c5156616fc34a6bf02d1bb174d0a457cee20c2 |

The holdout script (T08) must reuse `code/03_build_panel.py` and `code/04_estimation.py` unchanged and apply the specification above, with the threshold 15.07 hardcoded.

## Open items (not blocking)
Per-meeting release times (UNVERIFIED), press-conference flag completion, final cluster definition (year is a proxy for volatility episodes).
