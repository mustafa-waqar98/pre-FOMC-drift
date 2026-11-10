# Reproducibility. The holdout scripts (08, 09) are run-once and deliberately NOT in `all`.
PY = python3 -I
.PHONY: all test dev report paper
all: test dev report paper
test:
	for t in tests/test_*.py; do python3 $$t || exit 1; done
dev:
	$(PY) code/05_dev_premium.py
	$(PY) code/06_dev_calm_anxious.py
	$(PY) code/11_sensitivity_dev.py
report:  # reads saved T08/T09 raw outputs only
	$(PY) code/10_report.py
	cp output/figures/*.pdf paper/figures/
paper:
	cd paper && latexmk -pdf -interaction=nonstopmode main.tex
