"""T09: exploratory-secondary tests on the holdout (VIX-change, press-conference subsample, robustness). Does not alter the primary result."""
import importlib.util
import numpy as np, pandas as pd
def _load(n, f):
    s = importlib.util.spec_from_file_location(n, f); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
bp, est = _load("bp", "code/03_build_panel.py"), _load("est", "code/04_estimation.py")
THR, B = 15.07, 1e4
p = bp.build(".", allow_holdout=True).sort_values("date").reset_index(drop=True)
p["r"] = np.log(p["px_1345"] / p["px_1600"].shift(1)) - p["rf"]
p["r_nf"] = np.log(p["px_1345"] / p["px_1600"].shift(1))
v = p["vix"].ffill(); p["vix_lag"] = v.shift(5); p["dvix"] = v.shift(1) - v.shift(5)  # VIX change over the week ending the day before
p["ok"] = (p["valid"] == 1) & (p["valid"].shift(1, fill_value=0) == 1) & p["r"].notna() & p["vix_lag"].notna() & p["dvix"].notna()
h = p[p.date >= "2020-01-01"]
f = h[(h.fomc == 1) & h.ok].copy(); f["anx"] = (f.vix_lag > THR).astype(int); f["yr"] = f.date.dt.year
pc = pd.read_csv("data/raw/fomc_meetings_2021_2026.csv", parse_dates=["meeting_date"])[["meeting_date", "press_conference"]]
f = f.merge(pc, left_on="date", right_on="meeting_date", how="left")
def fit(d, lab, xcol=None, thr=None):
    y = d.r.values * B; cl = d.yr.values
    if len(d) < 5 or len(set(cl)) < 2: print(f"{lab:34s} n={len(d)} too small"); return
    if xcol:
        X = np.column_stack([np.ones(len(d)), d[xcol].values]); b, se, _ = est.ols_cluster(y, X, cl)
        print(f"{lab:34s} n={len(d):3d} a={b[0]:7.1f} slope={b[1]:6.2f} (se {se[1]:.2f}, t={b[1]/se[1]:.2f}) wildp={est.wild_cluster_bootstrap_p(y, X, cl, 1, B=999, seed=1)}"); return
    a = d.anx.values if thr is None else (d.vix_lag.values > thr).astype(int)
    if a.sum() < 3: print(f"{lab:34s} n={len(d)} anxious n={a.sum()} too small"); return
    pa, sa = est.premium_anxious(y, a, cl)
    Xa = np.column_stack([np.ones(len(d)), 1 - a])
    print(f"{lab:34s} n={len(d):3d} nAnx={a.sum():3d} mean={y.mean():6.1f} anxPrem={pa:6.1f} (se {sa:.1f}) wildp={est.wild_cluster_bootstrap_p(y, Xa, cl, 0, B=999, seed=1)}")
print("== VIX-change test: r = a + c*dVIX (dVIX = VIX[t-1]-VIX[t-5], points) [exploratory]")
fit(f, "all", "dvix")
X = np.column_stack([np.ones(len(f)), f.vix_lag, f.dvix]); b, se, _ = est.ols_cluster(f.r.values * B, X, f.yr.values)
print(f"joint level+change: c_level={b[1]:.2f} (t={b[1]/se[1]:.2f}) c_change={b[2]:.2f} (t={b[2]/se[2]:.2f})")
print("== Press-conference subsample (flag known only 2021+; 2020 UNVERIFIED -> excluded)")
print("flag counts:", f.press_conference.value_counts(dropna=False).to_dict())
fit(f[f.press_conference == 1], "press=1 anxious premium")
fit(f[f.press_conference == 0], "press=0 anxious premium")
fit(f[f.date >= "2021-01-01"], "2021+ (flag-known sample)")
print("== Robustness (anxious premium a+b, wild p for a+b=0)")
fit(f, "baseline thr 15.07")
for t in (18, 20, 25): fit(f, f"threshold {t}", thr=t)
fit(f, "holdout-median threshold", thr=float(f.vix_lag.median()))
for y_ in sorted(f.yr.unique()): fit(f[f.yr != y_], f"drop {y_}")
fit(f[f.yr != 2020], "excl 2020 (covid)")
g = f.copy(); lo, hi = np.percentile(g.r, [5, 95]); g["r"] = g.r.clip(lo, hi); fit(g, "winsorized 5/95")
g = f.copy(); g["r"] = (p.loc[p.date.isin(f.date), "r_nf"].values); fit(g, "no rf adjustment")
