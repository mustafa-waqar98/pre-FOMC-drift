# Referee-style self review (T12, 2026-11-09)

Build: `cd paper && latexmk -pdf main.tex` compiles with no errors, no undefined citations or references, no overfull boxes.

## Main concerns
1. Calm cell has n=9 in the holdout, so the state contrast b is weakly identified; the paper must keep describing it as under-powered (it does).
2. Only seven episode clusters: wild-bootstrap p-values are the headline inference; the continuous VIX slope (t=2.48) should not be read as a rejection.
3. Matched-VIX placebo (Fed minus non-Fed +55.5 bps) shows a meeting-window return, not a state-dependent one; keep the interpretation paragraph scoped to that.
4. Secondary tests (T09) are exploratory and run once; none rejects at 5%. No press=0 meetings exist, so the press-conference comparison cannot be made.
5. Holdout was run once (T08); no rerun is permitted.

## Fix list (open, UNVERIFIED items)
- F1 Lucca-Moench headline numbers: verify at primary source.
- F2 Martello-Ribeiro 109 / 9.7 bps figures: verify at primary source.
- F3 Per-meeting release times (design.tex): verify from Fed primary pages.
- F4 2020 press-conference flag: verify.
- F5 Backlog B4 (Makefile, environment file, data dictionary) and B5 (sensitivity design) remain unchecked.
