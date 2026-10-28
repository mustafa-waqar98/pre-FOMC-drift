"""Estimation toolkit (numpy only). Meeting-level spec: r = a + b*Anxious + X g + e.

Functions are data-agnostic; real data enter at T05+ via the dev-only panel.
"""
import numpy as np


def ols_cluster(y, X, cl):
    """OLS with CR1 cluster-robust covariance. Returns beta, se, resid."""
    y, X, cl = np.asarray(y, float), np.asarray(X, float), np.asarray(cl)
    n, k = X.shape
    xtx_inv = np.linalg.inv(X.T @ X)
    b = xtx_inv @ X.T @ y
    e = y - X @ b
    ids = np.unique(cl)
    S = np.zeros((k, k))
    for g in ids:
        s = X[cl == g].T @ e[cl == g]
        S += np.outer(s, s)
    G = len(ids)
    c = G / (G - 1) * (n - 1) / (n - k) if G > 1 else 1.0
    V = c * xtx_inv @ S @ xtx_inv
    return b, np.sqrt(np.diag(V)), e


def design(anxious, controls=None):
    cols = [np.ones(len(anxious)), np.asarray(anxious, float)]
    if controls is not None:
        cols += list(np.atleast_2d(np.asarray(controls, float).T))
    return np.column_stack(cols)


def premium_anxious(y, anxious, cl, controls=None):
    """Premium in anxious meetings a+b with cluster SE (linear combination, controls at zero)."""
    X = design(anxious, controls)
    y, cl = np.asarray(y, float), np.asarray(cl)
    k = X.shape[1]
    xtx_inv = np.linalg.inv(X.T @ X)
    b = xtx_inv @ X.T @ y
    e = y - X @ b
    S = np.zeros((k, k))
    ids = np.unique(cl)
    for g in ids:
        s = X[cl == g].T @ e[cl == g]
        S += np.outer(s, s)
    G, n = len(ids), len(y)
    V = (G / (G - 1) if G > 1 else 1) * (n - 1) / (n - k) * xtx_inv @ S @ xtx_inv
    w = np.zeros(k); w[0] = w[1] = 1
    return float(w @ b), float(np.sqrt(w @ V @ w))


def wild_cluster_bootstrap_p(y, X, cl, j, B=999, seed=0):
    """Wild cluster bootstrap-t p-value (Rademacher weights, null imposed) for H0: beta_j = 0."""
    rng = np.random.default_rng(seed)
    y, X, cl = np.asarray(y, float), np.asarray(X, float), np.asarray(cl)
    b, se, _ = ols_cluster(y, X, cl)
    t0 = b[j] / se[j]
    keep = [i for i in range(X.shape[1]) if i != j]
    Xr = X[:, keep]
    br = np.linalg.lstsq(Xr, y, rcond=None)[0]
    fit, er = Xr @ br, y - Xr @ br
    ids, inv = np.unique(cl, return_inverse=True)
    cnt = 0
    for _ in range(B):
        w = rng.choice([-1.0, 1.0], size=len(ids))[inv]
        yb = fit + er * w
        bb, sb, _ = ols_cluster(yb, X, cl)
        cnt += abs(bb[j] / sb[j]) >= abs(t0) - 1e-12
    return (cnt + 1) / (B + 1)


def permutation_placebo(fed_ret, fed_vix, nonfed_ret, nonfed_vix, B=2000, seed=0):
    """Placebo: for each Fed meeting draw a non-Fed day with nearest VIX (random among k=5 nearest).
    Returns observed mean(fed) - mean(matched), and a two-sided p from random relabelling of the pooled matched pairs."""
    rng = np.random.default_rng(seed)
    fr, fv = np.asarray(fed_ret, float), np.asarray(fed_vix, float)
    nr, nv = np.asarray(nonfed_ret, float), np.asarray(nonfed_vix, float)
    def match():
        idx = [rng.choice(np.argsort(np.abs(nv - v))[:5]) for v in fv]
        return nr[idx]
    obs = fr.mean() - match().mean()
    d = fr - match()
    cnt = 0
    for _ in range(B):
        s = rng.choice([-1.0, 1.0], size=len(d))
        cnt += abs((s * d).mean()) >= abs(d.mean()) - 1e-15
    return float(obs), (cnt + 1) / (B + 1)


def simulate_power(effect, n_clusters, per_cluster, sigma, rho, B=500, seed=0, alpha=0.05):
    """Power of H0: mean=0 with episode-clustered data: y = effect + u_g + e, ICC=rho, total sd=sigma.
    Test: |t| > 1.96 using cluster-robust SE (t_{G-1} critical value)."""
    from math import erf, sqrt
    rng = np.random.default_rng(seed)
    su, se_ = sigma * np.sqrt(rho), sigma * np.sqrt(1 - rho)
    cl = np.repeat(np.arange(n_clusters), per_cluster)
    X = np.ones((len(cl), 1))
    # t critical via simulation-free approximation: use normal-based crit scaled by t_{G-1} Cornish-Fisher
    z = 1.959964
    G = n_clusters
    crit = z + (z**3 + z) / (4 * (G - 1)) if G > 1 else np.inf
    rej = 0
    for _ in range(B):
        y = effect + rng.normal(0, su, n_clusters)[cl] + rng.normal(0, se_, len(cl))
        b, s, _ = ols_cluster(y, X, cl)
        rej += abs(b[0] / s[0]) > crit
    return rej / B


def minimum_detectable_effect(n_clusters, per_cluster, sigma, rho, power=0.8, B=400, seed=0):
    """Smallest effect (bisection on a grid) with simulated power >= target."""
    lo, hi = 0.0, 6 * sigma
    for _ in range(14):
        mid = (lo + hi) / 2
        if simulate_power(mid, n_clusters, per_cluster, sigma, rho, B, seed) >= power:
            hi = mid
        else:
            lo = mid
    return hi
