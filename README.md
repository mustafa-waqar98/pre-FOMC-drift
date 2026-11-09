# Pre-FOMC announcement drift after 2020

Does the pre-FOMC equity return drift reappear in high-uncertainty meetings after 2020, when publication and press-conference regime are held fixed?

Layout: `data/raw` (inputs, never edited), `data/processed` (derived panels), `code` (numbered pipeline), `output` (tables and figures), `paper` (LaTeX), `docs` (status and frozen spec).

Holdout discipline: the 2020 to 2026 outcome is not examined until `docs/SPEC_FROZEN.md` is committed.

## Build and status
Paper: `cd paper && latexmk -pdf main.tex` (output `paper/main.pdf`). Pipeline scripts are numbered in `code/`; raw estimator outputs are in `output/` (`T08_holdout_raw.txt`, `T09_secondary_raw.txt`). The specification is frozen (tag `spec-frozen`) and the holdout was run once. Open verification items are listed in `docs/REFEREE_REVIEW.md`.
