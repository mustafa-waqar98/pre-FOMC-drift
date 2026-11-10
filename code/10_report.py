"""T10: figures/tables from saved outputs only (no re-estimation). Numbers parsed from raw output files."""
import re, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
R8, R9 = open("output/T08_holdout_raw.txt").read(), open("output/T09_secondary_raw.txt").read()
m = pd.read_csv("output/tables/T08_meetings.csv"); m["bps"] = m.r * 1e4
d = pd.read_csv("output/tables/dev_meeting_returns.csv")
dcol = [c for c in d.columns if c.lower() in ("r", "ret", "bps")]
NAVY, BLUE, LIGHT, GREY = "#0B2545", "#2F6DB5", "#9DBDE0", "#5A6675"
plt.rcParams.update({"font.family": "serif", "font.size": 9, "axes.edgecolor": GREY, "axes.labelcolor": NAVY,
    "xtick.color": GREY, "ytick.color": GREY, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": "#E3E9F0", "grid.linewidth": .6, "axes.axisbelow": True, "legend.frameon": False})
# Figure 1: holdout meeting returns vs lagged VIX
fig, ax = plt.subplots(figsize=(5.5, 3.6))
for a_, c_, lb in [(0, LIGHT, "Calm (VIX $\\leq$ 15.07)"), (1, NAVY, "Anxious (VIX $>$ 15.07)")]:
    s_ = m[m.anx == a_]; ax.scatter(s_.vix_lag, s_.bps, c=c_, s=26, edgecolor="white", linewidth=.5, label=lb, zorder=3)
ax.axvline(15.07, ls="--", c=BLUE, lw=1); ax.axhline(0, c=GREY, lw=.8)
ax.set_xlabel("VIX five trading days before meeting"); ax.set_ylabel("Window return (bps)")
ax.set_title("Holdout FOMC windows, 2020\u20132026", fontsize=10, color=NAVY, loc="left")
ax.legend(fontsize=8, loc="upper left"); fig.tight_layout(); fig.savefig("output/figures/fig1_holdout_scatter.pdf"); plt.close(fig)
# Figure 2: calm vs anxious means, dev vs holdout
g = m.groupby("anx").bps.agg(["mean", "count", "sem"])
dev = {"calm": -6.6, "anxious": 19.3}  # from output/tables/T06_calm_anxious.txt
fig, ax = plt.subplots(figsize=(4.8, 3.4)); x = np.arange(2)
ax.bar(x - .2, [dev["calm"], dev["anxious"]], .38, color=LIGHT, label="Development 2010\u201319", zorder=3)
ax.bar(x + .2, [g.loc[0, "mean"], g.loc[1, "mean"]], .38, color=NAVY, label="Holdout 2020\u201326", zorder=3,
       yerr=[g.loc[0, "sem"], g.loc[1, "sem"]], error_kw=dict(ecolor=BLUE, capsize=3, lw=1))
ax.set_xticks(x); ax.set_xticklabels(["Calm", "Anxious"]); ax.axhline(0, c=GREY, lw=.8)
ax.set_ylabel("Mean window return (bps)"); ax.set_title("Mean window return by state (holdout bars: $\\pm$1 s.e.)", fontsize=9, color=NAVY, loc="left")
ax.legend(fontsize=8); fig.tight_layout(); fig.savefig("output/figures/fig2_state_means.pdf"); plt.close(fig)
# Figure 3: development-only sensitivity of the anxious premium (from output/tables/B5_sensitivity_dev.csv)
import os
if os.path.exists("output/tables/B5_sensitivity_dev.csv"):
    s = pd.read_csv("output/tables/B5_sensitivity_dev.csv")
    fig, ax = plt.subplots(figsize=(5.8, 3.2)); yy = np.arange(len(s))[::-1]
    ax.hlines(yy, 0, s.anxious_bps, color=LIGHT, lw=2, zorder=2); ax.scatter(s.anxious_bps, yy, c=NAVY, s=30, zorder=3)
    ax.set_yticks(yy); ax.set_yticklabels(s.variant, fontsize=7); ax.axvline(0, c=GREY, lw=.8)
    ax.set_xlabel("Anxious-state premium (bps), development 2010\u201319"); ax.grid(axis="y", visible=False)
    fig.tight_layout(); fig.savefig("output/figures/fig3_dev_sensitivity.pdf"); plt.close(fig)
# Table 1: robustness (parsed from T09 raw)
rows = re.findall(r"^(\S.*?)\s+n=\s*(\d+) nAnx=\s*(\d+) mean=\s*([-\d.]+) anxPrem=\s*([-\d.]+) \(se ([\d.]+)\) wildp=([\d.]+)", R9, re.M)
t = ["\\begin{tabular}{lrrrrr}\\toprule", "Specification & $n$ & $n_{\\mathrm{anx}}$ & Prem. (bps) & s.e. & Wild $p$ \\\\ \\midrule"]
for lab, n, na, mu, pr, se, p in rows:
    t.append(f"{lab.replace('_',' ').replace('%','\\%')} & {n} & {na} & {pr} & {se} & {p} \\\\")
t += ["\\bottomrule\\end{tabular}"]
open("paper/figures/tab_robust.tex", "w").write("\n".join(t))
# Table 2: primary holdout vs dev
f = lambda pat, s: re.search(pat, s).groups()
a, sa = f(r"calm a=([-\d.]+) \(se ([\d.]+)\)", R8); b, sb = f(r"b=([-\d.]+) \(se ([\d.]+)", R8)
ap, se_ap = f(r"a\+b=([-\d.]+) se=([\d.]+)", R8); pb = f(r"p\(b=0\)=([\d.]+)", R8)[0]; pab = f(r"p\(a\+b=0\)=([\d.]+)", R8)[0]
c, sc = f(r"c=([-\d.]+) \(se ([\d.]+)", R8); pl = re.findall(r"placebo (\w+)\s+n=\s*(\d+) fed-minus-matched=\s*([-\d.]+) bps p=([\d.]+)", R8)
t = ["\\begin{tabular}{lrr}\\toprule", " & Development & Holdout \\\\ \\midrule",
     f"Calm mean $a$ (bps) & $-6.6$ (3.3) & {a} ({sa}) \\\\", f"Anxious$-$calm $b$ (bps) & 26.0 (11.6) & {b} ({sb}) \\\\",
     f"Anxious premium $a+b$ (bps) & 19.3 (11.4) & {ap} ({se_ap}) \\\\", f"Wild-bootstrap $p(b=0)$ & 0.059 & {pb} \\\\",
     f"Wild-bootstrap $p(a+b=0)$ & --- & {pab} \\\\", f"VIX slope $c$ (bps/pt) & 1.60 (0.97) & {c} ({sc}) \\\\", "\\midrule"]
for k, n, v, p in pl: t.append(f"Placebo ({k}, $n={n}$): Fed$-$matched (bps) & --- & {v} ($p={p}$) \\\\")
t += ["\\bottomrule\\end{tabular}"]; open("paper/figures/tab_primary.tex", "w").write("\n".join(t))
print(g.round(1).to_string())
