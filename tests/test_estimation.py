"""Synthetic-data tests for the estimation toolkit."""
import importlib.util
from pathlib import Path
import numpy as np

spec = importlib.util.spec_from_file_location("est", Path(__file__).resolve().parents[1] / "code" / "04_estimation.py")
est = importlib.util.module_from_spec(spec); spec.loader.exec_module(est)

rng = np.random.default_rng(1)
# 1. OLS recovers known coefficients; cluster SE matches classical when clusters are singletons (up to CR1 factor)
n = 400
x = rng.integers(0, 2, n)
y = 0.5 + 1.0 * x + rng.normal(0, 1, n)
X = est.design(x)
b, se, _ = est.ols_cluster(y, X, np.arange(n))
assert abs(b[0] - 0.5) < 0.2 and abs(b[1] - 1.0) < 0.3
s2 = ((y - X @ b) ** 2).sum() / (n - 2)
classical = np.sqrt(np.diag(s2 * np.linalg.inv(X.T @ X)))
assert np.allclose(se, classical, rtol=0.15)

# 2. Clustering inflates SE when errors share a cluster component
G, m = 40, 10
cl = np.repeat(np.arange(G), m)
yc = rng.normal(0, 1, G)[cl] + rng.normal(0, 0.5, G * m)
Xc = np.ones((G * m, 1))
_, sec, _ = est.ols_cluster(yc, Xc, cl)
_, sei, _ = est.ols_cluster(yc, Xc, np.arange(G * m))
assert sec[0] > 2 * sei[0]

# 3. Wild bootstrap: small p under a true effect, large-ish p under null
xa = np.repeat(rng.integers(0, 2, G), m)
Xa = est.design(xa)
p_alt = est.wild_cluster_bootstrap_p(yc + 3 * xa, Xa, cl, 1, B=199)
p_null = est.wild_cluster_bootstrap_p(yc, Xa, cl, 1, B=199)
assert p_alt < 0.05
rej = 0
for _ in range(40):
    yn = rng.normal(0, 1, G)[cl] + rng.normal(0, 0.5, G * m)
    xn = np.repeat(rng.integers(0, 2, G), m)
    rej += est.wild_cluster_bootstrap_p(yn, est.design(xn), cl, 1, B=99) < 0.05
assert rej / 40 < 0.15

# 4. premium_anxious equals a+b
pa, pse = est.premium_anxious(yc + 2 * xa, xa, cl)
assert abs(pa - (yc + 2 * xa)[xa == 1].mean()) < 1e-8 and pse > 0

# 5. Placebo: no difference under null; detects a shift
nonv = rng.uniform(10, 30, 3000); nonr = rng.normal(0, 1, 3000)
fv = rng.uniform(10, 30, 80)
o0, p0 = est.permutation_placebo(rng.normal(0, 1, 80), fv, nonr, nonv, B=500)
o1, p1 = est.permutation_placebo(rng.normal(1.5, 1, 80), fv, nonr, nonv, B=500)
assert p0 > 0.05 and p1 < 0.01 and o1 > 1

# 6. Power: ~size at zero effect, monotone in effect, falls with ICC
p_0 = est.simulate_power(0.0, 20, 4, 1.0, 0.3, B=600)
p_big = est.simulate_power(1.5, 20, 4, 1.0, 0.3, B=300)
p_mid = est.simulate_power(0.5, 20, 4, 1.0, 0.3, B=300)
assert p_0 < 0.12 and p_big > 0.95 and p_big > p_mid
assert est.simulate_power(0.5, 20, 4, 1.0, 0.8, B=300) < p_mid
mde = est.minimum_detectable_effect(20, 4, 1.0, 0.3, B=200)
assert 0.3 < mde < 1.2
print("all estimation tests passed")
