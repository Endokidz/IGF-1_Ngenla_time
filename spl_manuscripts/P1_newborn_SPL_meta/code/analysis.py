"""
P1 — Meta-analysis of stretched penile length (SPL) in term newborns.

Inputs : data/term_extraction.csv (agent extraction, one row per study/subgroup)
Outputs: data/analysis_dataset.csv, data/results.json, figures/*.png

Analyses
  1. Study-level mean & SD (direct, or converted from median/IQR/range: Luo 2018 / Wan 2014)
  2. Random-effects (REML + HKSJ) pooled mean SPL with 95% CI and 95% prediction interval
  3. Random-effects pooled within-population SD on the log scale (Bartlett-corrected)
  4. Subgroups by WHO region; mixed-effects meta-regression (region, publication year,
     explicit fat-pad depression)
  5. Study-specific -2.5 SD thresholds; proportion of each population classified
     below the fixed 2.5 cm threshold implied by the 'classic' standard
  6. Small-study effects (Egger), leave-one-out, sensitivity analyses
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


def load():
    df = pd.read_csv(os.path.join(D, "term_extraction.csv"), dtype=str).fillna("")
    for c in ["n", "year", "mean_cm", "sd_cm", "median_cm", "q1_cm", "q3_cm", "min_cm", "max_cm", "se_cm"]:
        df[c] = num(df[c])
    PRINT_YEAR = {"Chikani2014": "Chikani 2015", "Badawy2021": "Badawy 2022", "Shah2020": "Shah 2021",
                  "Nanda2023": "Nanda 2024", "Singal2015": "Singal 2016", "Jarrett2013": "Jarrett 2014"}
    disp = lambda sid: PRINT_YEAR.get(sid, re.sub(r"(\D)(\d{4})$", r"\1 \2", sid))
    df["label"] = df.apply(lambda r: disp(r["study_id"]) + (f" ({r['subgroup_label']})" if r["subgroup_label"] else ""), axis=1)
    return df


def derive(df):
    rows = []
    for _, r in df.iterrows():
        n = r["n"]
        mean, sd, how = r["mean_cm"], r["sd_cm"], "reported"
        if (pd.isna(sd) or sd == 0) and not pd.isna(r["se_cm"]) and not pd.isna(n):
            sd, how = r["se_cm"] * math.sqrt(n), "SD_from_SE"
        if pd.isna(mean) or pd.isna(sd):
            try:
                m2, s2, how2 = meta.mean_sd_from_summary(
                    n, median=None if pd.isna(r["median_cm"]) else r["median_cm"],
                    q1=None if pd.isna(r["q1_cm"]) else r["q1_cm"], q3=None if pd.isna(r["q3_cm"]) else r["q3_cm"],
                    mn=None if pd.isna(r["min_cm"]) else r["min_cm"], mx=None if pd.isna(r["max_cm"]) else r["max_cm"])
                if pd.isna(mean):
                    mean = m2
                if pd.isna(sd):
                    sd = s2
                how = how2
            except Exception:
                pass
        rows.append(dict(mean=mean, sd=sd, derivation=how))
    out = pd.concat([df.reset_index(drop=True), pd.DataFrame(rows)], axis=1)
    tech = out["technique"].str.lower()
    out["fatpad_explicit"] = tech.str.contains(r"fat|pubic|symphys|bone|ramus|depress", regex=True).astype(int)
    out["fulltext"] = (out["source_level"].str.lower() == "fulltext").astype(int)
    return out


def apply_flags(df):
    fl = pd.read_csv(os.path.join(D, "curation_flags.csv"), dtype=str).fillna("")
    df["flags"] = ""
    for _, f in fl.iterrows():
        m = (df["study_id"] == f["study_id"]) & (df["subgroup_label"] == f["subgroup_label"])
        if not m.any():
            raise SystemExit(f"curation flag does not match any row: {f['study_id']} / {f['subgroup_label']}")
        df.loc[m, "flags"] = df.loc[m, "flags"] + f["flag"] + ";"
    df["mixed_ga"] = df["flags"].str.contains("mixed_ga")
    df["concern"] = df["flags"].str.contains("measurement_concern")
    return df


def main():
    df_all = apply_flags(derive(load()))
    df_all.to_csv(os.path.join(D, "all_rows_with_flags.csv"), index=False)
    PRIMARY = os.environ.get("P1_SET", "primary")
    if PRIMARY == "primary":
        df = df_all[~df_all["mixed_ga"]].copy()
    else:
        df = df_all.copy()
    usable = df[~df["mean"].isna() & ~df["n"].isna()].copy()
    usable["v_mean"] = usable["sd"] ** 2 / usable["n"]
    res = {"k_rows_extracted": int(len(df)), "k_rows_with_mean": int(len(usable))}

    # SD imputation (only for pooled-mean analysis) when SD unavailable: median SD
    med_sd = usable["sd"].median()
    usable["sd_imputed"] = usable["sd"].isna()
    usable.loc[usable["sd_imputed"], "v_mean"] = med_sd ** 2 / usable.loc[usable["sd_imputed"], "n"]
    res["median_sd_used_for_imputation"] = med_sd
    res["k_sd_imputed"] = int(usable["sd_imputed"].sum())
    usable.to_csv(os.path.join(D, "analysis_dataset.csv"), index=False)

    # 1. Pooled mean
    pm = meta.random_effects(usable["mean"], usable["v_mean"], "REML", hksj=True)
    res["pooled_mean"] = pm.as_dict()
    res["pooled_mean"]["tau2_ci"] = pm.tau2_ci
    # Primary excluding imputed SD
    u2 = usable[~usable["sd_imputed"]]
    pm2 = meta.random_effects(u2["mean"], u2["v_mean"], "REML", hksj=True)
    res["pooled_mean_no_imputed_sd"] = pm2.as_dict()

    # 2. Pooled SD (log scale)
    s = usable[~usable["sd_imputed"] & (usable["n"] > 1)].copy()
    s["y_lsd"] = np.log(s["sd"]) + 1 / (2 * (s["n"] - 1))
    s["v_lsd"] = 1 / (2 * (s["n"] - 1))
    ps = meta.random_effects(s["y_lsd"], s["v_lsd"], "REML", hksj=True)
    res["pooled_sd"] = dict(sd=math.exp(ps.mu), ci_lo=math.exp(ps.ci[0]), ci_hi=math.exp(ps.ci[1]),
                            pi_lo=math.exp(ps.pi[0]) if not math.isnan(ps.pi[0]) else None,
                            pi_hi=math.exp(ps.pi[1]) if not math.isnan(ps.pi[1]) else None,
                            I2=ps.I2, k=ps.k)

    # 3. Thresholds
    sd_p = res["pooled_sd"]["sd"]
    res["pooled_minus2p5sd_threshold_cm"] = pm.mu - 2.5 * sd_p
    # Predictive distribution of an individual newborn in a NEW population:
    # mean ~ N(mu, tau^2 + se^2); individual ~ N(mean, sd_p^2)
    res["predictive_individual_sd_cm"] = math.sqrt(pm.tau2 + pm.se ** 2 + sd_p ** 2)

    # 4. Region subgroups
    sub = {}
    for reg, g in usable.groupby("who_region"):
        if len(g) >= 2:
            r = meta.random_effects(g["mean"], g["v_mean"], "REML", hksj=True)
            gs = s[s["who_region"] == reg]
            sdr = math.exp(meta.random_effects(gs["y_lsd"], gs["v_lsd"], "REML", hksj=True).mu) if len(gs) >= 2 else (
                float(gs["sd"].iloc[0]) if len(gs) == 1 else float("nan"))
            sub[reg] = dict(k=r.k, n=int(g["n"].sum()), mu=r.mu, ci=r.ci, pi=r.pi, I2=r.I2, tau=r.tau,
                            sd_pooled=sdr, threshold=r.mu - 2.5 * sdr if not math.isnan(sdr) else None)
        else:
            g1 = g.iloc[0]
            sub[reg] = dict(k=1, n=int(g1["n"]), mu=float(g1["mean"]), ci=None, pi=None, I2=None, tau=None,
                            sd_pooled=float(g1["sd"]) if not pd.isna(g1["sd"]) else None,
                            threshold=float(g1["mean"] - 2.5 * g1["sd"]) if not pd.isna(g1["sd"]) else None)
    res["by_region"] = sub
    # Test for subgroup differences (Q_between under random effects with separate tau^2)
    regs = [k for k, v in sub.items() if v["k"] >= 2]
    if len(regs) >= 2:
        mus = np.array([sub[k]["mu"] for k in regs])
        ses = []
        for k in regs:
            g = usable[usable["who_region"] == k]
            ses.append(meta.random_effects(g["mean"], g["v_mean"], "REML", hksj=False).se)
        w = 1 / np.array(ses) ** 2
        mbar = np.sum(w * mus) / np.sum(w)
        Qb = float(np.sum(w * (mus - mbar) ** 2))
        res["subgroup_Q_between"] = dict(Q=Qb, df=len(regs) - 1, p=float(1 - stats.chi2.cdf(Qb, len(regs) - 1)))

    # 5. Meta-regression
    X, names = [], []
    regions = sorted(usable["who_region"].unique())
    ref_region = usable["who_region"].value_counts().idxmax()
    for reg in regions:
        if reg != ref_region:
            X.append((usable["who_region"] == reg).astype(float).values)
            names.append(f"region_{reg}_vs_{ref_region}")
    if X:
        mr_region = meta.meta_regression(usable["mean"], usable["v_mean"], np.column_stack(X), names)
        res["metareg_region"] = mr_region
    yr = usable["year"].values.astype(float)
    res["metareg_year_per_decade"] = meta.meta_regression(usable["mean"], usable["v_mean"], (yr - 2000) / 10, ["per_decade"])
    if usable["fatpad_explicit"].nunique() > 1:
        res["metareg_fatpad_explicit"] = meta.meta_regression(usable["mean"], usable["v_mean"],
                                                              usable["fatpad_explicit"].values, ["fatpad_explicit"])
    if usable["fulltext"].nunique() > 1:
        res["metareg_fulltext"] = meta.meta_regression(usable["mean"], usable["v_mean"], usable["fulltext"].values, ["fulltext"])

    # 6. Fixed 2.5 cm threshold applied to every population
    s2 = usable[~usable["sd_imputed"]].copy()
    s2["pct_below_2p5cm"] = 100 * stats.norm.cdf((2.5 - s2["mean"]) / s2["sd"])
    s2["own_threshold_cm"] = s2["mean"] - 2.5 * s2["sd"]
    s2[["label", "country", "who_region", "n", "mean", "sd", "own_threshold_cm", "pct_below_2p5cm"]].to_csv(
        os.path.join(D, "fixed_threshold_misclassification.csv"), index=False)
    res["pct_below_2p5cm_summary"] = dict(median=float(s2["pct_below_2p5cm"].median()),
                                          min=float(s2["pct_below_2p5cm"].min()),
                                          max=float(s2["pct_below_2p5cm"].max()),
                                          n_studies_above_2pct=int((s2["pct_below_2p5cm"] > 2).sum()),
                                          k=int(len(s2)))

    # 7. Small-study effects, leave-one-out, sensitivity
    if len(usable) >= 10:
        res["egger"] = dict(zip(["intercept", "se", "t", "p"], meta.egger_test(usable["mean"], usable["v_mean"])))
    loo = []
    for i in range(len(usable)):
        sub_ = usable.drop(usable.index[i])
        r = meta.random_effects(sub_["mean"], sub_["v_mean"], "REML", hksj=True)
        loo.append(dict(omitted=usable.iloc[i]["label"], mu=r.mu, lo=r.ci[0], hi=r.ci[1], I2=r.I2))
    pd.DataFrame(loo).to_csv(os.path.join(D, "leave_one_out.csv"), index=False)
    res["loo_range_mu"] = [min(x["mu"] for x in loo), max(x["mu"] for x in loo)]
    sens = {}
    for name, mask in {
        "fulltext_only": usable["fulltext"] == 1,
        "fatpad_explicit_only": usable["fatpad_explicit"] == 1,
        "n_ge_100": usable["n"] >= 100,
        "reported_mean_sd_only": usable["derivation"] == "reported",
        "exclude_measurement_concern": ~usable["concern"],
        "exclude_concern_and_abstract_only": (~usable["concern"]) & (usable["fulltext"] == 1),
    }.items():
        g = usable[mask]
        if len(g) >= 3:
            sens[name] = meta.random_effects(g["mean"], g["v_mean"], "REML", hksj=True).as_dict()
    allu = df_all[~df_all["mean"].isna() & ~df_all["n"].isna()].copy()
    allu["v_mean"] = allu["sd"].fillna(med_sd) ** 2 / allu["n"]
    sens["including_mixed_GA_rows"] = meta.random_effects(allu["mean"], allu["v_mean"], "REML", hksj=True).as_dict()
    sens["including_mixed_GA_rows"]["k_mixed_added"] = int(allu["mixed_ga"].sum())
    res["sensitivity"] = sens
    res["k_rows_total_extracted"] = int(len(df_all))
    res["k_rows_mixed_ga"] = int(df_all["mixed_ga"].sum())
    res["k_rows_no_n"] = int(df_all["n"].isna().sum())
    res["k_studies_primary"] = int(usable["study_id"].nunique())
    res["n_primary"] = int(usable["n"].sum())

    with open(os.path.join(D, "results.json"), "w") as f:
        json.dump(res, f, indent=2, default=lambda x: float(x) if isinstance(x, (np.floating, np.integer)) else str(x))

    # ---------------- Figures ----------------
    order = usable.sort_values(["who_region", "mean"]).reset_index(drop=True)
    lo = order["mean"] - 1.96 * np.sqrt(order["v_mean"])
    hi = order["mean"] + 1.96 * np.sqrt(order["v_mean"])
    w = 1 / (order["v_mean"] + pm.tau2)
    labs = [f"{r.label} [{r.who_region}]" for r in order.itertuples()]
    rt = [f"{r.mean:.2f} ({r.sd:.2f}) n={int(r.n)}" + ("*" if r.sd_imputed else "") for r in order.itertuples()]
    meta.forest_plot(labs, order["mean"].values, lo.values, hi.values, w.values, pm,
                     os.path.join(F, "Fig2_forest_mean_SPL.png"), "Mean stretched penile length (cm)",
                     right_text=rt)
    meta.funnel_plot(usable["mean"], usable["v_mean"], pm.mu, os.path.join(F, "FigS1_funnel.png"),
                     "Mean stretched penile length (cm)")
    # Fixed-threshold figure
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    o = s2.sort_values("pct_below_2p5cm")
    fig, ax = plt.subplots(figsize=(7.5, max(3.5, 0.25 * len(o) + 1.5)))
    ax.barh(range(len(o)), o["pct_below_2p5cm"], color="#2a78d6", height=0.7)
    ax.axvline(100 * stats.norm.cdf(-2.5), color="#b03a2e", ls="--", lw=1)
    ax.text(100 * stats.norm.cdf(-2.5), len(o) - 0.3, " nominal 0.62%", color="#b03a2e", fontsize=8, va="bottom")
    ax.set_yticks(range(len(o)))
    ax.set_yticklabels([f"{l} [{r}]" for l, r in zip(o["label"], o["who_region"])], fontsize=7.5)
    ax.set_xscale("symlog", linthresh=0.1)
    ax.set_xlabel("Expected % of newborns below the fixed 2.5 cm threshold (log scale)")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(F, "Fig3_fixed_threshold.png"), dpi=300)
    plt.close(fig)

    print(json.dumps({k: res[k] for k in ["k_rows_extracted", "k_rows_with_mean", "k_sd_imputed", "pooled_mean",
                                          "pooled_sd", "pooled_minus2p5sd_threshold_cm", "pct_below_2p5cm_summary"]},
                     indent=1, default=lambda x: round(float(x), 4) if isinstance(x, (float, np.floating)) else str(x)))


if __name__ == "__main__":
    main()
