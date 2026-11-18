"""
P2 — Meta-analysis of hormonal treatment for micropenis: change in SPL.

Inputs : data/arm_extraction.csv, data/ipd_extraction.csv
Outputs: data/analysis_arms.csv, data/results.json, figures/*

Effect measure: mean within-arm change in SPL (cm), post - pre.
Variance: SD_change^2 / n, where SD_change is
  (a) reported, else
  (b) computed from IPD for that study, else
  (c) derived from arm SDs and the pre-post correlation r estimated from the
      IPD pool (median of study-level r), with sensitivity r in {0.3, 0.5, 0.7, 0.9}
      (Cochrane Handbook section 6.5.2.8; Higgins 2024).
Arms reporting only median/range are converted (Luo 2018 / Wan 2014) and flagged.
Random effects REML + HKSJ; subgroup by intervention class; meta-regression
on age at start (infancy <= 24 mo vs later) and diagnosis (CHH vs other).
"""
import json
import math
import os
import re
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
num = lambda x: pd.to_numeric(x, errors="coerce")
CLASS_LABEL = {"IM_T": "IM testosterone", "topical_T": "Topical testosterone", "DHT": "DHT gel",
               "hCG": "hCG (± FSH)", "rGn_infusion": "Recombinant gonadotropins", "GnRH_pump": "Pulsatile GnRH",
               "other": "Other"}


def ipd_stats(ipd):
    out = {}
    for sid, g in ipd.groupby("study_id"):
        g = g.dropna(subset=["pre_cm", "post_cm"])
        if len(g) >= 3:
            d = g["post_cm"] - g["pre_cm"]
            r = np.corrcoef(g["pre_cm"], g["post_cm"])[0, 1] if g["pre_cm"].std() > 0 and g["post_cm"].std() > 0 else np.nan
            out[sid] = dict(n=len(g), pre_mean=g["pre_cm"].mean(), pre_sd=g["pre_cm"].std(ddof=1),
                            post_mean=g["post_cm"].mean(), post_sd=g["post_cm"].std(ddof=1),
                            change_mean=d.mean(), change_sd=d.std(ddof=1), r=r)
    return out


def build(arms, ipds, r_assumed):
    rows = []
    for _, a in arms.iterrows():
        n = a["n"]
        pre, post = a["pre_mean_cm"], a["post_mean_cm"]
        spre, spost = a["pre_sd_cm"], a["post_sd_cm"]
        chg, schg = a["change_mean_cm"], a["change_sd_cm"]
        how = []
        # IPD fallback for the whole arm when the arm row is incomplete
        ip = ipds.get(a["study_id"])
        if (pd.isna(pre) or pd.isna(post)) and ip and (pd.isna(n) or abs(ip["n"] - n) <= 1):
            pre, post, spre, spost = ip["pre_mean"], ip["post_mean"], ip["pre_sd"], ip["post_sd"]
            n = ip["n"] if pd.isna(n) else n
            how.append("arm_from_IPD")
        if pd.isna(chg) and not (pd.isna(pre) or pd.isna(post)):
            chg = post - pre
        if pd.isna(schg):
            if ip and (abs(ip["n"] - n) <= 1):
                schg = ip["change_sd"]
                how.append("SDchange_from_IPD")
            elif not (pd.isna(spre) or pd.isna(spost)):
                schg = meta.change_sd(spre, spost, r_assumed)
                how.append(f"SDchange_r={r_assumed}")
        else:
            how.append("SDchange_reported")
        rows.append(dict(a.to_dict(), n_used=n, pre=pre, post=post, change=chg, sd_change=schg,
                         derivation=";".join(how) or "reported"))
    df = pd.DataFrame(rows)
    df = df[~df["change"].isna() & ~df["sd_change"].isna() & ~df["n_used"].isna() & (df["n_used"] >= 2)].copy()
    df["v"] = df["sd_change"] ** 2 / df["n_used"]
    return df


def main():
    arms = pd.read_csv(os.path.join(D, "arm_extraction.csv"), dtype=str).fillna("")
    for c in ["n", "pre_mean_cm", "pre_sd_cm", "post_mean_cm", "post_sd_cm", "change_mean_cm", "change_sd_cm",
              "pre_sds_mean", "pre_sds_sd", "post_sds_mean", "post_sds_sd", "year", "age_mean_months"]:
        if c in arms:
            arms[c] = num(arms[c])
    try:
        ipd = pd.read_csv(os.path.join(D, "ipd_extraction.csv"), dtype=str).fillna("")
        for c in ["age_months", "pre_cm", "post_cm"]:
            ipd[c] = num(ipd[c])
    except FileNotFoundError:
        ipd = pd.DataFrame(columns=["study_id", "pre_cm", "post_cm"])
    ipds = ipd_stats(ipd)
    rs = [v["r"] for v in ipds.values() if not np.isnan(v["r"])]
    r_ipd = float(np.median(rs)) if rs else 0.5
    res = {"ipd_studies": {k: {kk: float(vv) for kk, vv in v.items()} for k, v in ipds.items()},
           "r_ipd_median": r_ipd, "r_ipd_values": rs}

    df = build(arms, ipds, r_ipd)
    df["class_label"] = df["intervention_class"].map(CLASS_LABEL).fillna(df["intervention_class"])
    df["infancy"] = df["age_at_start"].str.contains(r"month|mo\b|infan|neonat|newborn|week", case=False, regex=True) & \
        ~df["age_at_start"].str.contains(r"year|yr|y\b", case=False, regex=True)
    df.loc[~df["age_mean_months"].isna(), "infancy"] = df["age_mean_months"] <= 24
    df["chh"] = df["diagnosis"].str.contains(r"CHH|hypogonadotrop|Kallmann|HH\b|pituitary", case=False, regex=True)
    df.to_csv(os.path.join(D, "analysis_arms.csv"), index=False)
    res["k_arms_extracted"] = int(len(arms))
    res["k_arms_analysed"] = int(len(df))
    res["n_analysed"] = int(df["n_used"].sum())

    overall = meta.random_effects(df["change"], df["v"], "REML", hksj=True)
    res["overall"] = overall.as_dict()
    by = {}
    for cl, g in df.groupby("class_label"):
        if len(g) >= 2:
            r = meta.random_effects(g["change"], g["v"], "REML", hksj=True)
            by[cl] = r.as_dict() | {"n": int(g["n_used"].sum())}
        else:
            g1 = g.iloc[0]
            by[cl] = dict(k=1, mu=float(g1["change"]), ci_lo=float(g1["change"] - 1.96 * math.sqrt(g1["v"])),
                          ci_hi=float(g1["change"] + 1.96 * math.sqrt(g1["v"])), n=int(g1["n_used"]))
    res["by_class"] = by
    # Meta-regressions
    for name, x in {"infancy": df["infancy"].astype(float), "chh": df["chh"].astype(float)}.items():
        if x.nunique() > 1 and len(df) >= 5:
            res[f"metareg_{name}"] = meta.meta_regression(df["change"], df["v"], x.values, [name])
    # Class as categorical
    classes = df["class_label"].value_counts()
    refc = classes.idxmax()
    Xc, nm = [], []
    for c in classes.index:
        if c != refc and classes[c] >= 1:
            Xc.append((df["class_label"] == c).astype(float).values)
            nm.append(f"{c}_vs_{refc}")
    if Xc and len(df) - len(Xc) - 1 >= 2:
        res["metareg_class"] = meta.meta_regression(df["change"], df["v"], np.column_stack(Xc), nm)
    # Sensitivity to r for arms using imputed r
    sens = {}
    for r in (0.3, 0.5, 0.7, 0.9):
        d2 = build(arms, ipds, r)
        sens[str(r)] = meta.random_effects(d2["change"], d2["v"], "REML", hksj=True).as_dict()
    res["sensitivity_r"] = sens
    # Excluding abstract-only
    g = df[df["source_level"].str.lower().str.contains("full")]
    if len(g) >= 3:
        res["sensitivity_fulltext_only"] = meta.random_effects(g["change"], g["v"], "REML", hksj=True).as_dict()
    if len(df) >= 10:
        res["egger"] = dict(zip(["intercept", "se", "t", "p"], meta.egger_test(df["change"], df["v"])))
    # SDS-based analysis where available
    sds = arms[~arms["pre_sds_mean"].isna() & ~arms["post_sds_mean"].isna() & ~arms["n"].isna()].copy()
    if len(sds) >= 2:
        sds["chg"] = sds["post_sds_mean"] - sds["pre_sds_mean"]
        sds["sdc"] = [meta.change_sd(a, b, r_ipd) if not (pd.isna(a) or pd.isna(b)) else np.nan
                      for a, b in zip(sds["pre_sds_sd"], sds["post_sds_sd"])]
        sds = sds.dropna(subset=["sdc"])
        if len(sds) >= 2:
            sds["v"] = sds["sdc"] ** 2 / sds["n"]
            res["sds_change"] = meta.random_effects(sds["chg"], sds["v"], "REML", hksj=True).as_dict()
            res["sds_change"]["arms"] = sds["study_id"].tolist()

    with open(os.path.join(D, "results.json"), "w") as f:
        json.dump(res, f, indent=2, default=lambda x: float(x) if isinstance(x, (np.floating, np.integer)) else str(x))

    # Forest plot grouped by class
    o = df.sort_values(["class_label", "change"]).reset_index(drop=True)
    lo = o["change"] - stats.t.ppf(0.975, o["n_used"] - 1) * np.sqrt(o["v"])
    hi = o["change"] + stats.t.ppf(0.975, o["n_used"] - 1) * np.sqrt(o["v"])
    labs = [f"{r.study_id} — {r.class_label}" for r in o.itertuples()]
    rt = [f"{r.change:+.2f}  n={int(r.n_used)}" + ("†" if "r=" in r.derivation else "") for r in o.itertuples()]
    meta.forest_plot(labs, o["change"].values, lo.values, hi.values, (1 / (o["v"] + overall.tau2)).values, overall,
                     os.path.join(F, "Fig2_forest_change.png"), "Change in stretched penile length (cm)",
                     ref_line=0, right_text=rt)
    print(json.dumps({k: res[k] for k in ["k_arms_extracted", "k_arms_analysed", "n_analysed", "r_ipd_median", "overall", "by_class"]},
                     indent=1, default=lambda x: round(float(x), 3) if isinstance(x, (float, np.floating)) else str(x)))


if __name__ == "__main__":
    main()
