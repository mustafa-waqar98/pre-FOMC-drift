# Referee-style self review (T12, 2026-11-09)

Build: `cd paper && latexmk -pdf main.tex` compiles with no errors, no undefined citations or references, no overfull boxes.

## Main concerns
1. Calm cell has n=9 in the holdout, so the state contrast b is weakly identified; the paper must keep describing it as under-powered (it does).
2. Only seven episode clusters: wild-bootstrap p-values are the headline inference; the continuous VIX slope (t=2.48) should not be read as a rejection.
3. Matched-VIX placebo (Fed minus non-Fed +55.5 bps) shows a meeting-window return, not a state-dependent one; keep the interpretation paragraph scoped to that.
4. Secondary tests (T09) are exploratory and run once; none rejects at 5%. No press=0 meetings exist, so the press-conference comparison cannot be made.
5. Holdout was run once (T08); no rerun is permitted.

## Fix list (updated 2026-11-10)
- F1 Lucca-Moench: VERIFIED (about 49 bps, 24h window, 131 meetings, Sep 1994 to Mar 2011).
- F2 Martello: VERIFIED at the primary text (2018 PUC-Rio master's dissertation, sole author Martello; advisor Ribeiro; intro p.11 states 109 / 9.7 bps; baseline sample Sep 2003-Mar 2011, 60 meetings). Attribution corrected in the bibliography.
- F3 Release times: VERIFIED for 2011-2012 press-conference meetings (statement at 12:20-12:35 ET); 2:00 pm rule from 2013-03-13 confirmed. Eight dev meetings were mis-windowed; dev sensitivity reported in appendix; frozen spec and holdout unchanged.
- F4 2020 press-conference flag: VERIFIED (Fed lists a press conference at all 2020 meetings). T09 subsample not rerun (run-once rule).
- B4 and B5 done (Makefile, requirements, data dictionary, code/11_sensitivity_dev.py).
- F6 Added verified literature: Cieslak et al. 2019, Bernile et al. 2016, Kurov et al. 2019, Boguth et al. 2019.
- F7 Abstract written; amendment A1 documented in docs/AMENDMENT_A1.md and paper Section 5.1; figures restyled.
- Remaining limits (inherent): 7 year clusters, nine calm holdout meetings, futures instead of cash index, no pre-2010 intraday data, press-conference subsample excludes 2020 (run-once rule).
