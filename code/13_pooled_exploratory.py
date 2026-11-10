"""Exploratory (post-hoc, labelled as such): reads SAVED meeting-level files only, no re-estimation of the frozen
holdout run. (1) t(G-1) confidence intervals from the saved holdout estimates; (2) pooled development+holdout
test of the state contrast with a period fixed effect, year-clustered wild bootstrap."""
import importlib.util, re, json
import numpy as np, pandas as pd
from scipy import stats
s = importlib.util.spec_from_file_location("est", "code/04_estimation.py"); est = importlib.util.module_from_spec(s); s.loader.exec_module(est)
R8 = open("output/T08_holdout_raw.txt").read(); out = {}
a, sa = map(float, re.search(r"calm a=([-\d.]+) \(se ([\d.]+)\)", R8).groups())
b, sb = map(float, re.search(r"b=([-\d.]+) \(se ([\d.]+)", R8).groups())
ap, sap = map(float, re.search(r"a\+b=([-\d.]+) se=([\d.]+)", R8).groups())
t = stats.t.ppf(.975, 6)
for k, (e, se) in dict(calm=(a, sa), contrast=(b, sb), anxious=(ap, sap)).items(): out["holdout_ci95_" + k] = [e - t * se, e + t * se]
d = pd.read_csv("output/tables/dev_meeting_returns_corrected.csv"); h = pd.read_csv("output/tables/T08_meetings.csv")
d["hold"] = 0; h["hold"] = 1; P = pd.concat([d, h], ignore_index=True); y = P.r.values * 1e4; B = 1e4
X = est.design(P.anx.values, controls=P.hold.values)
bb, se, _ = est.ols_cluster(y, X, P.yr.values)
out.update(pooled_n=len(P), pooled_clusters=int(P.yr.nunique()), pooled_contrast=bb[1], pooled_contrast_se=se[1],
           pooled_contrast_wild_p=float(est.wild_cluster_bootstrap_p(y, X, P.yr.values, 1, B=999, seed=1)), pooled_period_shift=bb[2])
Xc = np.column_stack([np.ones(len(P)), P.vix_lag.values, P.hold.values]); bc, sc, _ = est.ols_cluster(y, Xc, P.yr.values)
out.update(pooled_slope=bc[1], pooled_slope_se=sc[1], pooled_slope_wild_p=float(est.wild_cluster_bootstrap_p(y, Xc, P.yr.values, 1, B=999, seed=2)))
json.dump(out, open("output/tables/pooled_exploratory.json", "w"), indent=1); print(json.dumps(out, indent=1))
