"""T05: dev-only (<=2019-12-31) pre-announcement premium and sub-period decline. ES grid, excess of rf."""
import importlib.util, sys
import numpy as np, pandas as pd
def _load(n, f):
    s = importlib.util.spec_from_file_location(n, f); m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
bp, est = _load("bp", "code/03_build_panel.py"), _load("est", "code/04_estimation.py")
p = bp.build(".")
assert p["date"].max() <= bp.CUTOFF
p = p.sort_values("date").reset_index(drop=True)
# window: previous valid session 16:00 print -> 14:00 (release 14:15, pre 2013-03) or 13:45 (release 14:00), 15 min buffer
end = np.where(p["date"] < "2013-03-01", p["px_1400"], p["px_1345"])
p["px_end"] = end
p["px_prev16"] = p["px_1600"].shift(1)
ok_prev = p["valid"].shift(1, fill_value=0) == 1
p["r"] = np.log(p["px_end"] / p["px_prev16"]) - p["rf"]
p["vix_lag"] = p["vix"].ffill().shift(5)   # one trading week before
p["ok"] = (p["valid"] == 1) & ok_prev & p["r"].notna() & p["vix_lag"].notna()
f = p[(p["fomc"] == 1) & p["ok"]].copy()
nf = p[(p["fomc"] == 0) & p["ok"]]
thr = f["vix_lag"].median()
f["anx"] = (f["vix_lag"] > thr).astype(int)
f["yr"] = f["date"].dt.year
bps = 1e4
print(f"FOMC meetings usable={len(f)} of {int(p['fomc'].sum())}; non-FOMC days={len(nf)}; VIX threshold (dev median)={thr:.2f}")
print(f"mean excess window return bps: FOMC={f.r.mean()*bps:.1f}  non-FOMC={nf.r.mean()*bps:.1f}")
def rep(lbl, d):
    y = d.r.values * bps
    b, se, _ = est.ols_cluster(y, np.ones((len(y), 1)), d.yr.values)
    print(f"{lbl:28s} n={len(d):3d} mean={b[0]:7.1f} bps  se(yr-cluster)={se[0]:5.1f}  t={b[0]/se[0]:5.2f}")
rep("all 2010-2019", f); rep("2010-2014", f[f.yr <= 2014]); rep("2015-2019", f[f.yr >= 2015])
rep("calm", f[f.anx == 0]); rep("anxious", f[f.anx == 1])
pa, se = est.premium_anxious(f.r.values * bps, f.anx.values, f.yr.values)
print(f"anxious premium a+b={pa:.1f} se={se:.1f}")
f[["date","r","vix_lag","anx","yr"]].to_csv("output/tables/dev_meeting_returns.csv", index=False)
