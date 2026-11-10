"""Post-freeze amendment A1 (dev only, <=2019-12-31): re-estimate the development benchmark with verified
release times. Eight 2011-2012 press-conference meetings released at 12:20-12:35 ET, so their window ends at
12:00 ET; all other meetings keep the frozen rule. VIX threshold stays 15.07 (VIX-based, unaffected).
Frozen scripts 03-06 and 08 are untouched; the holdout is not read here."""
import importlib.util, json
import numpy as np, pandas as pd
def _load(n, f):
    s = importlib.util.spec_from_file_location(n, f); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
bp, est = _load("bp", "code/03_build_panel.py"), _load("est", "code/04_estimation.py")
p = bp.build(".").sort_values("date").reset_index(drop=True)
assert p["date"].max() <= bp.CUTOFF
mid = pd.to_datetime(pd.read_csv("data/raw/fomc_release_times_verified.csv").meeting_date)
base = np.where(p["date"] < "2013-03-01", p["px_1400"], p["px_1345"])
p["px_end"] = np.where(p["date"].isin(mid), p["px_1200"], base)
p["r"] = np.log(p["px_end"] / p["px_1600"].shift(1)) - p["rf"]
p["vix_lag"] = p["vix"].ffill().shift(5)
p["ok"] = (p.valid == 1) & (p.valid.shift(1, fill_value=0) == 1) & p.r.notna() & p.vix_lag.notna()
f = p[(p.fomc == 1) & p.ok].copy(); nf = p[(p.fomc == 0) & p.ok].copy()
THR = 15.07; B = 1e4
f["anx"] = (f.vix_lag > THR).astype(int); f["yr"] = f.date.dt.year; y = f.r.values * B
out = {"n": len(f), "n_calm": int((f.anx == 0).sum()), "n_anx": int((f.anx == 1).sum()), "n_midday_in_sample": int(f.date.isin(mid).sum())}
def m1(d):
    b, se, _ = est.ols_cluster(d.r.values * B, np.ones((len(d), 1)), d.yr.values); return b[0], se[0]
for lbl, d in [("all", f), ("2010_14", f[f.yr <= 2014]), ("2015_19", f[f.yr >= 2015])]:
    out[lbl] = dict(zip(("mean", "se"), m1(d)), n=len(d))
X = est.design(f.anx.values); b, se, _ = est.ols_cluster(y, X, f.yr.values)
pa, sa = est.premium_anxious(y, f.anx.values, f.yr.values)
out.update(calm=b[0], calm_se=se[0], diff=b[1], diff_se=se[1], anx=pa, anx_se=sa,
           wild_p_diff=float(est.wild_cluster_bootstrap_p(y, X, f.yr.values, 1, B=999, seed=1)))
Xc = np.column_stack([np.ones(len(f)), f.vix_lag.values]); bc, sc, _ = est.ols_cluster(y, Xc, f.yr.values)
out.update(slope=bc[1], slope_se=sc[1])
nfr, nfv = nf.r.values * B, nf.vix_lag.values
for lbl, d in [("all", f), ("anxious", f[f.anx == 1]), ("calm", f[f.anx == 0])]:
    o, pv = est.permutation_placebo(d.r.values * B, d.vix_lag.values, nfr, nfv, B=2000, seed=2); out["placebo_" + lbl] = dict(diff=o, p=pv)
sd_all, sd_c, sd_a = y.std(ddof=1), y[f.anx.values == 0].std(ddof=1), y[f.anx.values == 1].std(ddof=1)
g = f.groupby("yr").r.apply(lambda s: s.values * B); k = np.mean([len(v) for v in g]); G = len(g)
ms_b = sum(len(v) * (v.mean() - y.mean()) ** 2 for v in g) / (G - 1); ms_w = sum(((v - v.mean()) ** 2).sum() for v in g) / (len(y) - G)
rho = max(0.0, (ms_b - ms_w) / (ms_b + (k - 1) * ms_w))
out.update(sd_all=sd_all, sd_calm=sd_c, sd_anx=sd_a, icc=rho,
           mde_all=est.minimum_detectable_effect(7, 8, sd_all, rho, B=300, seed=3),
           mde_anx=est.minimum_detectable_effect(7, 4, sd_a, rho, B=300, seed=3))
json.dump(out, open("output/tables/dev_corrected.json", "w"), indent=1)
f[["date", "r", "vix_lag", "anx", "yr"]].to_csv("output/tables/dev_meeting_returns_corrected.csv", index=False)
print(json.dumps(out, indent=1))
