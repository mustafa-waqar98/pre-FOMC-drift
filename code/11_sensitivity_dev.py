"""B5: pre-specified sensitivity grid, DEV ONLY (<=2019-12-31). Alternative window ends and removal of
press-conference meetings Apr-2011..Dec-2012 whose statement was released near 12:30 ET (release time
verified for 2012-09-13 only; others UNVERIFIED). Threshold = dev median VIX. Not run on the holdout."""
import importlib.util
import numpy as np, pandas as pd
def _load(n, f):
    s = importlib.util.spec_from_file_location(n, f); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
bp, est = _load("bp", "code/03_build_panel.py"), _load("est", "code/04_estimation.py")
p = bp.build(".").sort_values("date").reset_index(drop=True)
assert p["date"].max() <= bp.CUTOFF
MIDDAY = pd.to_datetime(["2011-04-27","2011-06-22","2011-11-02","2012-01-25","2012-04-25","2012-06-20","2012-09-13","2012-12-12"])
p["vix_lag"] = p["vix"].ffill().shift(5)
base_end = np.where(p["date"] < "2013-03-01", p["px_1400"], p["px_1345"])
variants = {
 "baseline (era rule 1400/1345)": (base_end, False),
 "end 13:45 all meetings": (p["px_1345"].values, False),
 "end 13:30 all meetings": (p["px_1330"].values, False),
 "end 12:00 all meetings": (p["px_1200"].values, False),
 "baseline, drop 8 midday-release meetings": (base_end, True),
 "end 12:00 for 8 midday meetings, else baseline": (np.where(p["date"].isin(MIDDAY), p["px_1200"], base_end), False),
}
B = 1e4; rows = []
for name, (pe, drop) in variants.items():
    q = p.copy(); q["r"] = np.log(pe / q["px_1600"].shift(1)) - q["rf"]
    q["ok"] = (q.valid == 1) & (q.valid.shift(1, fill_value=0) == 1) & q.r.notna() & q.vix_lag.notna()
    f = q[(q.fomc == 1) & q.ok].copy()
    if drop: f = f[~f.date.isin(MIDDAY)]
    f["anx"] = (f.vix_lag > 15.07).astype(int); f["yr"] = f.date.dt.year
    y = f.r.values * B; X = est.design(f.anx.values)
    b, se, _ = est.ols_cluster(y, X, f.yr.values)
    pa, sa = est.premium_anxious(y, f.anx.values, f.yr.values)
    pw = est.wild_cluster_bootstrap_p(y, X, f.yr.values, 1, B=999, seed=1)
    rows.append((name, len(f), y.mean(), b[0], pa, b[1], pw))
    print(f"{name:48s} n={len(f):3d} mean={y.mean():6.1f} calm={b[0]:6.1f} anx={pa:6.1f} diff={b[1]:6.1f} wild_p={pw:.3f}")
pd.DataFrame(rows, columns=["variant","n","mean_bps","calm_bps","anxious_bps","diff_bps","wild_p"]).to_csv("output/tables/B5_sensitivity_dev.csv", index=False)
