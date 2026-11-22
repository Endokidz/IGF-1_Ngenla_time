"""
P3 — Systematic review: adiposity and penile length in children (SWiM synthesis).

Quantities computed here (all from extracted, verbatim-sourced values):
  * Lee 2024: mean difference in SPL (high vs normal BMI) with 95% CI (Welch)
  * Ma 2025: within-arm change in SPL (paired SD not reported -> CI bounded
    under r = 0.5 and r = 0.8 assumptions)
  * Referral series: proportion of 'micropenis' referrals not confirmed
    (Wilson 95% CI); exploratory random-effects pooled proportion (logit, REML+HKSJ)
  * Effect-direction plot (SWiM item 'vote counting by direction of effect')
"""
import json
import math
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "common"))
import meta  # noqa: E402

D = os.path.join(HERE, "..", "data")
F = os.path.join(HERE, "..", "figures")
os.makedirs(F, exist_ok=True)
res = {}


def wilson(x, n, z=1.959964):
    p = x / n
    den = 1 + z ** 2 / n
    c = (p + z ** 2 / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z ** 2 / (4 * n ** 2)) / den
    return p, c - h, c + h


# 1. Lee 2024 (A02): SPL 5.17 +/- 1.77 (n=851) vs 4.99 +/- 1.48 (n=648)
m1, s1, n1 = 5.17, 1.77, 851
m2, s2, n2 = 4.99, 1.48, 648
md = m2 - m1
se = math.sqrt(s1 ** 2 / n1 + s2 ** 2 / n2)
df_w = (s1 ** 2 / n1 + s2 ** 2 / n2) ** 2 / ((s1 ** 2 / n1) ** 2 / (n1 - 1) + (s2 ** 2 / n2) ** 2 / (n2 - 1))
t = stats.t.ppf(0.975, df_w)
sp = math.sqrt(((n1 - 1) * s1 ** 2 + (n2 - 1) * s2 ** 2) / (n1 + n2 - 2))
res["Lee2024_md_cm"] = dict(md=md, lo=md - t * se, hi=md + t * se, smd=md / sp,
                            p=float(2 * (1 - stats.t.cdf(abs(md / se), df_w))))

# 2. Ma 2025 (A07): within-arm SPL change; paired SD unknown -> bounds
ma = {"PI+MNWL": (3.75, 0.76, 4.98, 0.64, 40), "MNWL": (4.03, 0.84, 4.40, 0.76, 40)}
res["Ma2025_change"] = {}
for arm, (a, sa, b, sb, n) in ma.items():
    out = {"change": b - a}
    for r in (0.5, 0.8):
        sdc = meta.change_sd(sa, sb, r)
        h = stats.t.ppf(0.975, n - 1) * sdc / math.sqrt(n)
        out[f"ci_r{r}"] = (b - a - h, b - a + h)
    res["Ma2025_change"][arm] = out

# 3. Referral series: 'micropenis' referrals not confirmed
ref = [("Khadilkar2025", 41, 96, "buried penis secondary to obesity"),
       ("Oyenusi2025", 16, 83, "SPL within reference range"),
       ("Aslan2013", 20, 65, "micropenis not confirmed")]
rows = []
for k, x, n, defn in ref:
    p, lo, hi = wilson(x, n)
    rows.append(dict(study=k, x=x, n=n, definition=defn, p=p, lo=lo, hi=hi))
rdf = pd.DataFrame(rows)
y = np.log(rdf.x / (rdf.n - rdf.x))
v = 1 / rdf.x + 1 / (rdf.n - rdf.x)
pr = meta.random_effects(y, v, "REML", hksj=True)
inv = lambda z: 1 / (1 + math.exp(-z))
res["referral_pooled_exploratory"] = dict(p=inv(pr.mu), lo=inv(pr.ci[0]), hi=inv(pr.ci[1]),
                                          pi_lo=inv(pr.pi[0]), pi_hi=inv(pr.pi[1]), I2=pr.I2, k=pr.k,
                                          tau=pr.tau)
res["referral_series"] = rows
rdf.to_csv(os.path.join(D, "referral_series_proportions.csv"), index=False)

# 4. Effect-direction table (coded from extraction; see manuscript Table 2)
#    direction: -1 = shorter with higher adiposity, 0 = no association, +1 = longer, NA = unclear
ed = pd.DataFrame([
    # study, n, outcome, fat pad depressed?, design, direction, source
    ("Lee 2024", 1499, "SPL", "Yes", "Group comparison", -1, "Full text"),
    ("Mancini 2021", 1130, "Non-stretched length", "No", "Group comparison", -1, "Abstract"),
    ("Zhang 2013", 206, "Non-stretched length", "Unclear", "Group comparison*", -1, "Abstract (Chinese)"),
    ("Zhang 2015", 3546, "Penile length", "Unclear", "Group comparison", -1, "Abstract (Chinese)"),
    ("Han 2026", 60, "Penile length", "Unclear", "Group comparison", -1, "Abstract"),
    ("Zhang 1997", None, "Penile length", "Unclear", "Group comparison", +1, "Abstract (Chinese)"),
    ("Camurdan 2007", 1040, "SPL (raw)", "Unclear", "Correlation", +1, "Abstract"),
    ("Fawaz 2021", 2972, "SPL z-score", "Unclear", "Correlation", +1, "Abstract"),
    ("Ishii 2014", 1628, "SPL z-score", "Unclear", "Correlation", 0, "Abstract"),
    ("Roy 2019", 460, "SPL", "Yes", "Correlation", 0, "Full text"),
    ("Bhat 2015", 250, "SPL", "Unclear", "Correlation", 0, "Full text"),
    ("Joya 2026", 210, "SPL", "Unclear", "Correlation", 0, "Abstract"),
    ("Arian 2025", 300, "SPL", "Unclear", "Correlation", 0, "Abstract"),
    ("Soydan 2012", 1539, "Penile length", "Unclear", "Regression", None, "Abstract"),
    ("Ma 2025 (weight loss)", 120, "SPL", "Unclear", "Before-after", -1, "Abstract (Chinese)"),
], columns=["study", "n", "outcome", "fatpad", "design", "direction", "source"])
ed.to_csv(os.path.join(D, "effect_direction.csv"), index=False)
tab = ed.groupby(["fatpad", "direction"], dropna=False).size()
res["effect_direction_counts"] = {f"{k[0]}|{k[1]}": int(v) for k, v in tab.items()}

with open(os.path.join(D, "results.json"), "w") as f:
    json.dump(res, f, indent=2, default=float)
print(json.dumps(res, indent=1, default=lambda x: round(float(x), 4)))

# ---- Figure: effect-direction plot ---------------------------------------
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

order = ed.copy()
order["grp"] = order["design"].map(lambda d: 0 if "Group" in d else (1 if d in ("Correlation", "Regression") else 2))
order = order.sort_values(["grp", "fatpad", "study"]).reset_index(drop=True)
fig, ax = plt.subplots(figsize=(8.6, 0.36 * len(order) + 1.4))
cols = ["Study", "n", "Outcome", "Fat pad\ndepressed", "Design", "Direction", "Source"]
xs = [0.0, 0.25, 0.33, 0.55, 0.66, 0.82, 0.90]
for x, c in zip(xs, cols):
    ax.text(x, len(order) + 0.2, c, fontsize=8, fontweight="bold", va="bottom")
for i, r in order.iterrows():
    yy = len(order) - 1 - i
    if i % 2 == 0:
        ax.add_patch(plt.Rectangle((-0.01, yy - 0.45), 1.12, 0.9, color="#f3f2ef", zorder=0))
    ax.text(xs[0], yy, r.study, fontsize=8, va="center")
    ax.text(xs[1], yy, "" if pd.isna(r.n) else f"{int(r.n):,}", fontsize=8, va="center")
    ax.text(xs[2], yy, r.outcome, fontsize=7.5, va="center")
    ax.text(xs[3], yy, r.fatpad, fontsize=8, va="center")
    ax.text(xs[4], yy, r.design, fontsize=7.5, va="center")
    cx = xs[5] + 0.03
    ms = 40 + 110 * (0 if pd.isna(r.n) else min(1, math.log10(max(r.n, 10)) / 3.6))
    if pd.isna(r.direction):
        ax.scatter([cx], [yy], s=ms, marker="o", facecolors="none", edgecolors="#52514e", linewidths=1)
        ax.text(cx, yy, "?", fontsize=6.5, ha="center", va="center", color="#52514e")
    elif r.direction == 0:
        ax.scatter([cx], [yy], s=ms, marker="o", color="#8a8984")
    elif r.direction < 0:
        ax.scatter([cx], [yy], s=ms, marker="v", color="#eb6834")
    else:
        ax.scatter([cx], [yy], s=ms, marker="^", color="#2a78d6")
    ax.text(xs[6], yy, r.source, fontsize=7.5, va="center")
ax.set_xlim(-0.01, 1.12)
ax.set_ylim(-0.8, len(order) + 0.9)
ax.axis("off")
ax.text(0.0, -0.75, "▼ shorter with higher adiposity   ▲ longer   ● no association   ? direction not reported.  "
        "Marker size ∝ log(n).  *Obese group pre-selected for micropenis.", fontsize=7, color="#52514e")
fig.tight_layout()
fig.savefig(os.path.join(F, "Fig2_effect_direction.png"), dpi=300)
plt.close(fig)
print("figure written")
