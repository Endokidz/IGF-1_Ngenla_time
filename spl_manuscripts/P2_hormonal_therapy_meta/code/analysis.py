"""
P2 — Meta-analysis of hormonal treatment for micropenis: change in SPL (cm).

Every arm's inclusion decision and derivation is coded explicitly below
(CURATION), so that the analysis is auditable line by line. Source values are
read from data/arm_extraction.csv and data/ipd_extraction.csv (verbatim-sourced).

Pre-specified rules
  R1 overlapping cohorts: keep the larger cohort (sensitivity: swap)
  R2 exclude: erect-length outcome; unpaired pre/post subsets; adult-majority
     cohorts; pubertal induction (different construct); arms without n
  R3 medians converted to mean/SD only when IQR or range given (Luo 2018; Wan 2014)
  R4 SD of change: reported > IPD > derived with r = median IPD pre-post r
     (sensitivity r in {0.3, 0.5, 0.7, 0.9})
Analysis: random effects (REML, HKSJ CI, 95% PI), by therapeutic group; meta-
regression on group; benchmark against regression to the mean (Paper 4).
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

A = pd.read_csv(os.path.join(D, "arm_extraction.csv"), dtype=str).fillna("").set_index("study_id")
I = pd.read_csv(os.path.join(D, "ipd_extraction.csv"), dtype=str).fillna("")
for c in ("pre_cm", "post_cm"):
    I[c] = pd.to_numeric(I[c], errors="coerce")
f = lambda sid, col: float(A.loc[sid, col]) if A.loc[sid, col] != "" else float("nan")

GROUPS = {
    "INF_GN": "Gonadotropin replacement in infancy (CHH)",
    "T_CHILD": "Testosterone (IM), infancy/childhood",
    "DHT": "Dihydrotestosterone gel",
    "ORAL_TU": "Oral testosterone undecanoate (DSD/hypospadias)",
    "HCG_CHILD": "hCG ± hMG, childhood IHH",
}

# --- IPD statistics ---------------------------------------------------------
ipd = {}
for sid, g in I.groupby("study_id"):
    g = g.dropna(subset=["pre_cm", "post_cm"])
    if len(g) >= 3:
        d = g.post_cm - g.pre_cm
        ipd[sid] = dict(n=len(g), pre_mean=g.pre_cm.mean(), pre_sd=g.pre_cm.std(ddof=1), post_mean=g.post_cm.mean(),
                        post_sd=g.post_cm.std(ddof=1), change=d.mean(), change_sd=d.std(ddof=1),
                        r=float(np.corrcoef(g.pre_cm, g.post_cm)[0, 1]))
R_IPD = float(np.median([ipd[s]["r"] for s in ("Lambert2025", "Sheng2025")]))


def from_median_iqr(n, med, q1, q3):
    return meta.mean_sd_from_summary(n, median=med, q1=q1, q3=q3)[:2]


def from_median_range(n, med, lo, hi):
    return meta.mean_sd_from_summary(n, median=med, mn=lo, mx=hi)[:2]


def arms(r):
    """Return list of curated arm dicts using pre-post correlation r where needed."""
    out = []

    def add(sid, group, n, change, sd_change, how, include=True, reason="", pre=None, post=None):
        out.append(dict(arm=sid, group=group, group_label=GROUPS.get(group, group), n=n, change=change,
                        sd_change=sd_change, derivation=how, include_primary=include, reason=reason,
                        pre=pre, post=post, source_level=A.loc[sid, "source_level"] if sid in A.index else ""))

    def prepost(sid, group, n=None, change=None, **kw):
        n = n or int(float(A.loc[sid, "n"]))
        pre, sp, post, so = f(sid, "pre_mean_cm"), f(sid, "pre_sd_cm"), f(sid, "post_mean_cm"), f(sid, "post_sd_cm")
        ch = change if change is not None else post - pre
        add(sid, group, n, ch, meta.change_sd(sp, so, r), f"pre/post SDs, r={r:.2f}", pre=pre, post=post, **kw)

    # ---- Gonadotropin replacement in infancy (CHH) ----
    L = ipd["Lambert2025"]
    add("Lambert2025", "INF_GN", L["n"], L["change"], L["change_sd"], "IPD (Table 4)", pre=L["pre_mean"], post=L["post_mean"])
    m1, s1 = from_median_iqr(9, 2.0, 1.8, 2.65)
    m2, s2 = from_median_iqr(9, 4.4, 4.0, 4.6)
    add("MesasArostegui2024", "INF_GN", 9, m2 - m1, meta.change_sd(s1, s2, r), f"median/IQR->mean/SD; r={r:.2f}", pre=m1, post=m2)
    m1, s1 = from_median_range(10, 2.0, 1.5, 2.5)
    m2, s2 = from_median_range(10, 3.8, 3.2, 4.5)
    add("Papadimitriou2019", "INF_GN", 10, m2 - m1, meta.change_sd(s1, s2, r), f"median/range->mean/SD; r={r:.2f}", pre=m1, post=m2)
    prepost("Stoupa2017", "INF_GN", n=5)
    prepost("Wang2025", "INF_GN")  # GnRH pump; stretch not stated (flag)
    # ---- Testosterone (IM), infancy/childhood ----
    hm, hs = from_median_iqr(37, 1.5, 0.9, 1.55)   # Harada: median change 15.0 mm [9.0-15.5]
    add("Harada2025", "T_CHILD", 37, hm, hs, "median/IQR of change -> mean/SD", pre=2.2, post=3.5)
    prepost("Karrou2023_TE", "T_CHILD", change=f("Karrou2023_TE", "change_mean_cm"))
    prepost("Kohva2019", "T_CHILD")
    prepost("Luo2003", "T_CHILD")
    # ---- DHT ----
    prepost("Karrou2023_DHT", "DHT", change=f("Karrou2023_DHT", "change_mean_cm"))
    prepost("Xu2017", "DHT")
    # ---- Oral TU ----
    prepost("Liu2021_5ARD", "ORAL_TU")
    prepost("Liu2024_PAIS", "ORAL_TU")
    add("Chen2015", "ORAL_TU", 34, f("Chen2015", "change_mean_cm"), f("Chen2015", "change_sd_cm"), "change SD reported")
    # ---- hCG, childhood IHH ----
    S = ipd["Sheng2025"]
    add("Sheng2025", "HCG_CHILD", S["n"], S["change"], S["change_sd"], "IPD (paired)", pre=S["pre_mean"], post=S["post_mean"])
    # ---- Excluded from primary (sensitivity / narrative) ----
    prepost("Wen2023_5ARD", "ORAL_TU", include=False, reason="R1 overlap with Liu2021_5ARD (smaller)")
    prepost("Wen2026_PAIS", "ORAL_TU", include=False, reason="R1 overlap with Liu2024_PAIS (smaller)")
    add("Liu2021_CHH_hCGhMG", "HCG_ADOL", 20, 2.2, 1.6, "change SD reported", include=False, reason="R2 erect length")
    add("Liu2021_CHH_GnRH", "GNRH_ADOL", 21, 1.0, 0.8, "change SD reported", include=False, reason="R2 erect length")
    prepost("Kim2011", "HCG_ADOL", include=False, reason="R2 adult-majority cohort (mean 18.9 y)")
    add("Agarwal2020_T", "T_ADOL", 12, 7.4 - 4.63, float("nan"), "unpaired", include=False, reason="R2 unpaired pre/post subsets")
    add("Tack2023_pubertalTRT", "T_ADOL", 7, f("Tack2023_pubertalTRT", "change_mean_cm"), f("Tack2023_pubertalTRT", "change_sd_cm"),
        "change SD reported", include=False, reason="R2 pubertal induction (anorchia)")
    return out


res = {"R_IPD": R_IPD, "ipd": ipd}
df = pd.DataFrame(arms(R_IPD))
df["v"] = df.sd_change ** 2 / df.n
df.to_csv(os.path.join(D, "curated_arms.csv"), index=False)
prim = df[df.include_primary].copy()
res["k_primary"] = int(len(prim))
res["n_primary"] = int(prim.n.sum())

overall = meta.random_effects(prim.change, prim.v, "REML", hksj=True)
res["overall"] = overall.as_dict()
by = {}
for g, sub in prim.groupby("group"):
    if len(sub) >= 2:
        r_ = meta.random_effects(sub.change, sub.v, "REML", hksj=True)
        by[g] = r_.as_dict() | {"n": int(sub.n.sum()), "label": GROUPS[g]}
    else:
        x = sub.iloc[0]
        h = stats.t.ppf(0.975, x.n - 1) * math.sqrt(x.v)
        by[g] = dict(k=1, mu=float(x.change), ci_lo=float(x.change - h), ci_hi=float(x.change + h), n=int(x.n), label=GROUPS[g])
res["by_group"] = by
# Meta-regression on group (reference: INF_GN)
levels = [g for g in prim.group.unique() if g != "INF_GN"]
X = np.column_stack([(prim.group == g).astype(float) for g in levels])
res["metareg_group"] = meta.meta_regression(prim.change, prim.v, X, levels)
# Karrou RCT: DHT vs TE (between-arm difference in change)
kd, kt = prim[prim.arm == "Karrou2023_DHT"].iloc[0], prim[prim.arm == "Karrou2023_TE"].iloc[0]
diff = kd.change - kt.change
se = math.sqrt(kd.v + kt.v)
res["Karrou_DHT_minus_TE"] = dict(diff=diff, lo=diff - 1.96 * se, hi=diff + 1.96 * se,
                                  p=float(2 * (1 - stats.norm.cdf(abs(diff / se)))))
# Sensitivity: r
sens = {}
for rr in (0.3, 0.5, 0.7, 0.9):
    d2 = pd.DataFrame(arms(rr))
    d2 = d2[d2.include_primary]
    d2["v"] = d2.sd_change ** 2 / d2.n
    sens[f"r={rr}"] = meta.random_effects(d2.change, d2.v, "REML", hksj=True).as_dict()
# Swap overlapping cohorts
sw = df[(df.include_primary & ~df.arm.isin(["Liu2021_5ARD", "Liu2024_PAIS"])) | df.arm.isin(["Wen2023_5ARD", "Wen2026_PAIS"])]
sens["swap_overlapping_cohorts"] = meta.random_effects(sw.change, sw.v, "REML", hksj=True).as_dict()
ft = prim[prim.source_level.str.contains("full")]
sens["fulltext_only"] = meta.random_effects(ft.change, ft.v, "REML", hksj=True).as_dict()
nc = prim[~prim.derivation.str.contains("median")]
sens["exclude_median_converted"] = meta.random_effects(nc.change, nc.v, "REML", hksj=True).as_dict()
nw = prim[~prim.arm.isin(["Wang2025", "Sheng2025"])]
sens["exclude_flagged_Wang_Sheng"] = meta.random_effects(nw.change, nw.v, "REML", hksj=True).as_dict()
res["sensitivity"] = sens
res["egger"] = dict(zip(["intercept", "se", "t", "p"], meta.egger_test(prim.change, prim.v)))
# Proportional change (post/pre) where available
pp = prim.dropna(subset=["pre", "post"])
res["proportional_change_median_pct"] = float(np.median(100 * (pp.post / pp.pre - 1)))
res["proportional_change_by_group"] = {g: float(np.median(100 * (s.post / s.pre - 1))) for g, s in pp.groupby("group")}
# Durability: Lambert 2025 early adolescence vs end of CSGI (IPD notes)
ea = I[I.study_id == "Lambert2025"].notes.str.extract(r"early adolescence SPL (\d+) mm")[0].astype(float) / 10
res["Lambert2025_early_adolescence_cm"] = dict(median=float(ea.median()), min=float(ea.min()), max=float(ea.max()))
# Benchmarks (Paper 4): regression to the mean in SD units -> cm using a newborn SD 0.4 cm and a childhood SD 0.6 cm
res["RTM_benchmark_cm"] = {lam: {"newborn_sd0.4": rtm * 0.4, "child_sd0.6": rtm * 0.6}
                           for lam, rtm in (("0.25", 0.166), ("0.5", 0.579), ("0.75", 1.072))}

with open(os.path.join(D, "results.json"), "w") as fh:
    json.dump(res, fh, indent=2, default=lambda x: float(x) if isinstance(x, (np.floating, np.integer)) else str(x))

# ---- Forest plot by group ----
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

order = ["INF_GN", "T_CHILD", "DHT", "ORAL_TU", "HCG_CHILD"]
rows = []
for g in order:
    sub = prim[prim.group == g].sort_values("change", ascending=False)
    rows.append(("H", GROUPS[g], None))
    for _, x in sub.iterrows():
        rows.append(("S", x.arm, x))
    rows.append(("P", g, by[g]))
fig, ax = plt.subplots(figsize=(8.6, 0.30 * len(rows) + 1.8))
y = len(rows)
yt, yl = [], []
for kind, lab, x in rows:
    y -= 1
    if kind == "H":
        ax.text(-0.95, y, lab, fontsize=8.5, fontweight="bold", va="center",
                bbox=dict(facecolor="white", edgecolor="none", pad=0.5))
        continue
    if kind == "S":
        h = stats.t.ppf(0.975, x.n - 1) * math.sqrt(x.v)
        ax.plot([x.change - h, x.change + h], [y, y], color="#333", lw=1)
        ax.scatter([x.change], [y], marker="s", s=12 + 3 * x.n ** 0.9, color="#2a78d6", zorder=3)
        disp = lab.replace("_", " ")
        yt.append(y); yl.append(f"   {disp}")
        ax.text(5.75, y, f"{x.change:+.2f} [{x.change-h:+.2f}, {x.change+h:+.2f}]  n={int(x.n)}", fontsize=7, va="center")
    if kind == "P" and x["k"] == 2:
        yt.append(y); yl.append("   Not pooled (k = 2)")
        continue
    if kind == "P":
        p = x
        lo, hi = p["ci_lo"], p["ci_hi"]
        ax.fill([lo, p["mu"], hi, p["mu"]], [y, y + 0.3, y, y - 0.3], color="#eb6834")
        yt.append(y); yl.append("   Subtotal" + (f" (k={p['k']})" if p["k"] > 1 else ""))
        ax.text(5.75, y, f"{p['mu']:+.2f} [{lo:+.2f}, {hi:+.2f}]", fontsize=7, va="center", fontweight="bold")
y -= 1.2
ax.fill([overall.ci[0], overall.mu, overall.ci[1], overall.mu], [y, y + 0.35, y, y - 0.35], color="#b03a2e")
ax.plot([overall.pi[0], overall.pi[1]], [y - 0.6, y - 0.6], color="#b03a2e", lw=2, alpha=0.5)
yt.append(y); yl.append(f"All arms (k={overall.k})")
ax.text(5.75, y, f"{overall.mu:+.2f} [{overall.ci[0]:+.2f}, {overall.ci[1]:+.2f}]", fontsize=7.5, va="center", fontweight="bold")
ax.axvline(0, color="grey", lw=0.8)
ax.axvspan(0, 0.23, color="#e9e8e4", zorder=0)
ax.text(0.115, y - 1.05, "RTM, λ=0.5", fontsize=6.5, ha="center", va="center", color="#52514e")
ax.set_yticks(yt)
ax.set_yticklabels(yl, fontsize=7.5)
ax.set_xlim(-1.0, 5.6)
ax.set_ylim(y - 1.2, len(rows) + 0.3)
ax.set_xlabel("Change in stretched penile length, cm (post − pre)")
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(os.path.join(F, "Fig2_forest_by_group.png"), dpi=300, bbox_inches="tight")
plt.close(fig)

print(json.dumps({k: res[k] for k in ("R_IPD", "k_primary", "n_primary", "overall", "by_group", "Karrou_DHT_minus_TE",
                                       "proportional_change_by_group", "Lambert2025_early_adolescence_cm")},
                 indent=1, default=lambda x: round(float(x), 3) if isinstance(x, (float, np.floating)) else str(x)))
