"""T06: dev-only (<=2019-12-31) calm/anxious split, matched-VIX placebo, power recalibrated on realized volatility."""
import importlib.util
import numpy as np, pandas as pd
def _load(n, f):
    s = importlib.util.spec_from_file_location(n, f); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
bp, est = _load("bp", "code/03_build_panel.py"), _load("est", "code/04_estimation.py")
p = bp.build(".").sort_values("date").reset_index(drop=True)
assert p["date"].max() <= bp.CUTOFF
p["px_end"] = np.where(p["date"] < "2013-03-01", p["px_1400"], p["px_1345"])
p["r"] = np.log(p["px_end"] / p["px_1600"].shift(1)) - p["rf"]
p["vix_lag"] = p["vix"].ffill().shift(5)
p["ok"] = (p["valid"] == 1) & (p["valid"].shift(1, fill_value=0) == 1) & p["r"].notna() & p["vix_lag"].notna()
f = p[(p.fomc == 1) & p.ok].copy(); nf = p[(p.fomc == 0) & p.ok].copy()
thr = f.vix_lag.median(); f["anx"] = (f.vix_lag > thr).astype(int); f["yr"] = f.date.dt.year
B = 1e4; y = f.r.values * B
print(f"n_meetings={len(f)} thr={thr:.2f} n_calm={(f.anx==0).sum()} n_anx={(f.anx==1).sum()}")
# split and interaction
X = est.design(f.anx.values); b, se, _ = est.ols_cluster(y, X, f.yr.values)
print(f"calm a={b[0]:.1f} (se {se[0]:.1f}); anxious-calm diff b={b[1]:.1f} (se {se[1]:.1f}, t={b[1]/se[1]:.2f})")
pa, sa = est.premium_anxious(y, f.anx.values, f.yr.values); print(f"anxious premium a+b={pa:.1f} se={sa:.1f}")
pw = est.wild_cluster_bootstrap_p(y, X, f.yr.values, 1, B=999, seed=1); print(f"wild cluster bootstrap p(diff=0)={pw if np.isscalar(pw) else pw}")
# continuous VIX
Xc = np.column_stack([np.ones(len(f)), f.vix_lag.values]); bc, sc, _ = est.ols_cluster(y, Xc, f.yr.values)
print(f"continuous: a={bc[0]:.1f} c={bc[1]:.2f} per VIX pt (se {sc[1]:.2f}, t={bc[1]/sc[1]:.2f})")
# placebo: matched-VIX non-FOMC days, all and by regime
nfr = nf.r.values * B; nfv = nf.vix_lag.values
for lbl, d in [("all", f), ("anxious", f[f.anx == 1]), ("calm", f[f.anx == 0])]:
    o, pv = est.permutation_placebo(d.r.values * B, d.vix_lag.values, nfr, nfv, B=2000, seed=2)
    print(f"placebo {lbl:8s} n={len(d):3d} fed-minus-matched={o:7.1f} bps  p={pv:.3f}")
# realized-volatility calibration
sd_all = y.std(ddof=1); sd_nf = nfr.std(ddof=1)
sd_c, sd_a = y[f.anx.values == 0].std(ddof=1), y[f.anx.values == 1].std(ddof=1)
g = f.groupby("yr").r.apply(lambda s: s.values * B)
k = np.mean([len(v) for v in g]); G = len(g)
ms_b = sum(len(v) * (v.mean() - y.mean()) ** 2 for v in g) / (G - 1)
ms_w = sum(((v - v.mean()) ** 2).sum() for v in g) / (len(y) - G)
rho = max(0.0, (ms_b - ms_w) / (ms_b + (k - 1) * ms_w))
print(f"realized sd bps: meetings={sd_all:.1f} calm={sd_c:.1f} anx={sd_a:.1f} non-FOMC={sd_nf:.1f}; ICC(year)={rho:.3f}; mean meetings/yr={k:.1f}, years={G}")
rows = []
for lbl, G_, k_, sg in [("dev full (10 yrs)", 10, 8, sd_all), ("holdout all (7 yrs x 8)", 7, 8, sd_all),
                       ("holdout anxious half (7 yrs x 4)", 7, 4, sd_a), ("holdout anxious half, sd=calm sd", 7, 4, sd_c)]:
    mde = est.minimum_detectable_effect(G_, k_, sg, rho, B=300, seed=3); rows.append((lbl, G_, k_, sg, mde))
    print(f"MDE(80% power) {lbl:34s} G={G_} k={k_} sd={sg:.1f} -> {mde:.1f} bps")
pd.DataFrame(rows, columns=["design", "clusters", "per_cluster", "sd_bps", "mde_bps"]).to_csv("output/tables/T06_power.csv", index=False)
f[["date", "r", "vix_lag", "anx", "yr"]].to_csv("output/tables/T06_meetings.csv", index=False)
