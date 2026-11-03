"""T08: frozen-spec holdout (scheduled FOMC meetings 2020-01-01 onward). Run ONCE. Threshold hardcoded."""
import importlib.util
import numpy as np, pandas as pd
def _load(n, f):
    s = importlib.util.spec_from_file_location(n, f); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
bp, est = _load("bp", "code/03_build_panel.py"), _load("est", "code/04_estimation.py")
THR, B = 15.07, 1e4
p = bp.build(".", allow_holdout=True).sort_values("date").reset_index(drop=True)
p["r"] = np.log(p["px_1345"] / p["px_1600"].shift(1)) - p["rf"]
p["vix_lag"] = p["vix"].ffill().shift(5)
p["ok"] = (p["valid"] == 1) & (p["valid"].shift(1, fill_value=0) == 1) & p["r"].notna() & p["vix_lag"].notna()
h = p[p.date >= "2020-01-01"]
f = h[(h.fomc == 1) & h.ok].copy(); nf = h[(h.fomc == 0) & h.ok].copy()
f["anx"] = (f.vix_lag > THR).astype(int); f["yr"] = f.date.dt.year
y = f.r.values * B
print(f"HOLDOUT n_meetings={len(f)} (scheduled in range={int((h.fomc==1).sum())}) thr={THR} n_calm={(f.anx==0).sum()} n_anx={(f.anx==1).sum()} years={sorted(f.yr.unique())}")
print(f"all-meeting mean={y.mean():.1f} bps sd={y.std(ddof=1):.1f}")
X = est.design(f.anx.values); b, se, _ = est.ols_cluster(y, X, f.yr.values)
print(f"calm a={b[0]:.1f} (se {se[0]:.1f}); b={b[1]:.1f} (se {se[1]:.1f}, t={b[1]/se[1]:.2f})")
pa, sa = est.premium_anxious(y, f.anx.values, f.yr.values); print(f"H1/H2 anxious premium a+b={pa:.1f} se={sa:.1f} t={pa/sa:.2f}; dev anxious 19.3")
print(f"wild bootstrap p(b=0)={est.wild_cluster_bootstrap_p(y, X, f.yr.values, 1, B=999, seed=1)}")
Xa = np.column_stack([np.ones(len(f)), 1 - f.anx.values])  # coef0 = anxious premium a+b
print(f"wild bootstrap p(a+b=0)={est.wild_cluster_bootstrap_p(y, Xa, f.yr.values, 0, B=999, seed=1)}")
Xc = np.column_stack([np.ones(len(f)), f.vix_lag.values]); bc, sc, _ = est.ols_cluster(y, Xc, f.yr.values)
print(f"continuous: a={bc[0]:.1f} c={bc[1]:.2f} (se {sc[1]:.2f}, t={bc[1]/sc[1]:.2f})")
for lbl, d in [("all", f), ("anxious", f[f.anx == 1]), ("calm", f[f.anx == 0])]:
    o, pv = est.permutation_placebo(d.r.values * B, d.vix_lag.values, nf.r.values * B, nf.vix_lag.values, B=2000, seed=2)
    print(f"placebo {lbl:8s} n={len(d):3d} fed-minus-matched={o:7.1f} bps p={pv:.3f}")
f[["date", "r", "vix_lag", "anx", "yr"]].to_csv("output/tables/T08_meetings.csv", index=False)
