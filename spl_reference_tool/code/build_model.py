"""
Build the SPL reference database and pooled models for the calculator.

Inputs (all verbatim-sourced extractions):
  ../../spl_manuscripts/P1_newborn_SPL_meta/data/all_rows_with_flags.csv   (term newborns)
  ../data/age_extraction.csv                                                (age bins, 1 mo-18 y)
  ../data/tanner_extraction.csv, ../data/tanner_extraction_from_age_studies.csv
  ../data/digitized_*.csv (optional; points digitised from published figures)

Outputs:
  ../data/reference_rows.csv      every usable row with mean/SD and derivation method
  ../app/model.json               pooled age curve, Tanner-stage pools, per-study rows
  ../figures/pooled_curve.png     diagnostic plot

Statistical model (age):
  y_i = ln(mean_i), v_i = (SD_i/mean_i)^2 / n_i            (delta method)
  y_i = B(t_i) beta + u_i + e_i,  u_i ~ N(0, tau^2), e_i ~ N(0, v_i)
  t = ln(age_years + 0.25); B = natural cubic spline basis (knots at quantiles of t)
  tau^2 by REML; CIs Knapp-Hartung. tau is the between-study (between-population and
  between-method) heterogeneity on the log scale, i.e. a relative spread of means.
  Within-population SD: ln(SD_i) + 1/(2(n_i-1)) on the same basis, variance 1/(2(n_i-1)).
Tanner: random-effects pooled mean (log) and log-SD per genital stage G1..G5.
"""
import json
import math
import os
import re
import sys

import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import minimize_scalar

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, os.path.join(ROOT, "..", "spl_manuscripts", "common"))
import meta  # noqa: E402

DATA = os.path.join(ROOT, "data")
APP = os.path.join(ROOT, "app")
FIG = os.path.join(ROOT, "figures")
for d in (APP, FIG):
    os.makedirs(d, exist_ok=True)
num = lambda x: pd.to_numeric(x, errors="coerce")
ZP = {3: 1.880794, 5: 1.644854, 10: 1.281552, 25: 0.674490}


# ---------------------------------------------------------------------------
# 1. Row normalisation
# ---------------------------------------------------------------------------

def to_mean_sd(r):
    n = r.get("n")
    mean, sd = r.get("mean_cm"), r.get("sd_cm")
    if pd.notna(mean) and pd.notna(sd) and sd > 0:
        return mean, sd, "reported mean/SD"
    if pd.notna(mean) and pd.notna(r.get("se_cm", np.nan)) and pd.notna(n):
        return mean, r["se_cm"] * math.sqrt(n), "SD from SE"
    # symmetric percentile pairs (widest available)
    for p in (3, 5, 10, 25):
        lo, hi = r.get(f"p{p}_cm"), r.get(f"p{100 - p}_cm")
        if pd.notna(lo) and pd.notna(hi) and hi > lo:
            med = r.get("p50_cm") if pd.notna(r.get("p50_cm")) else r.get("median_cm")
            m = mean if pd.notna(mean) else (med if pd.notna(med) else (lo + hi) / 2)
            return m, (hi - lo) / (2 * ZP[p]), f"SD from P{p}-P{100 - p} (normal)"
    if pd.notna(r.get("lms_M")) and pd.notna(r.get("lms_S")):
        M, S = r["lms_M"], r["lms_S"]
        return M, M * S, "LMS: mean~M, SD~M*S"
    if pd.notna(n):
        med = r.get("median_cm") if pd.notna(r.get("median_cm")) else r.get("p50_cm")
        try:
            m2, s2, how = meta.mean_sd_from_summary(
                n, median=med if pd.notna(med) else None,
                q1=r.get("p25_cm") if pd.notna(r.get("p25_cm")) else None,
                q3=r.get("p75_cm") if pd.notna(r.get("p75_cm")) else None,
                mn=r.get("min_cm") if pd.notna(r.get("min_cm")) else None,
                mx=r.get("max_cm") if pd.notna(r.get("max_cm")) else None)
            return (mean if pd.notna(mean) else m2), s2, how
        except Exception:
            pass
    return (mean if pd.notna(mean) else np.nan), np.nan, "no SD derivable"


def age_mid(r):
    if pd.notna(r.get("age_mean_years")):
        return float(r["age_mean_years"])
    lo, hi = r.get("age_lo_years"), r.get("age_hi_years")
    if pd.notna(lo) and pd.notna(hi):
        return (lo + hi) / 2
    if pd.notna(lo):
        return lo + 0.5
    return np.nan


NUMCOLS = ["n", "mean_cm", "sd_cm", "se_cm", "median_cm", "p3_cm", "p5_cm", "p10_cm", "p25_cm", "p50_cm", "p75_cm",
           "p90_cm", "p95_cm", "p97_cm", "min_cm", "max_cm", "lms_L", "lms_M", "lms_S", "age_lo_years", "age_hi_years",
           "age_mean_years", "tanner_stage", "year"]


def read(path, kind):
    if not os.path.exists(path):
        return pd.DataFrame()
    d = pd.read_csv(path, dtype=str).fillna("")
    for c in NUMCOLS:
        if c in d:
            d[c] = num(d[c])
        else:
            d[c] = np.nan
    d["kind"] = kind
    return d


def load_rows():
    frames = []
    # term newborns from P1 (primary rows only: excludes mixed GA; rows with no n kept for lookup)
    p1 = os.path.join(ROOT, "..", "spl_manuscripts", "P1_newborn_SPL_meta", "data", "all_rows_with_flags.csv")
    if os.path.exists(p1):
        d = pd.read_csv(p1, dtype=str).fillna("")
        d = d[~d["flags"].str.contains("mixed_ga")].copy()
        for c in NUMCOLS:
            d[c] = num(d[c]) if c in d else np.nan
        d["age_lo_years"], d["age_hi_years"], d["age_mean_years"] = 0.0, 28 / 365.25, 3 / 365.25
        d["age_bin_label"] = "term newborn (" + d["age_at_measurement"] + ")"
        d["kind"] = "newborn"
        d["fatpad_depressed"] = np.where(d["technique"].str.contains("fat|depress|pubic|ramus|symphys|bone", case=False),
                                         "yes/anchored", "unclear")
        d["measurement_concern"] = d["flags"].str.contains("measurement_concern")
        frames.append(d)
    frames.append(read(os.path.join(DATA, "age_extraction.csv"), "age"))
    t1 = read(os.path.join(DATA, "tanner_extraction.csv"), "tanner")
    t2 = read(os.path.join(DATA, "tanner_extraction_from_age_studies.csv"), "tanner")
    frames += [t1, t2]
    for f in sorted(os.listdir(DATA)):
        if f.startswith("digitized_") and f.endswith("_bins.csv"):
            frames.append(read(os.path.join(DATA, f), "digitized"))
    rows = pd.concat([f for f in frames if len(f)], ignore_index=True, sort=False)
    rows = rows.drop(columns=[c for c in ("mean", "sd", "derivation", "age", "v_mean", "sd_imputed", "label")
                              if c in rows.columns])
    if "measurement_concern" not in rows:
        rows["measurement_concern"] = False
    rows["measurement_concern"] = rows["measurement_concern"].fillna(False).astype(bool)
    out = []
    for _, r in rows.iterrows():
        m, s, how = to_mean_sd(r)
        out.append(dict(mean=m, sd=s, derivation=how, age=age_mid(r)))
    rows = pd.concat([rows.reset_index(drop=True), pd.DataFrame(out)], axis=1)
    return rows


# ---------------------------------------------------------------------------
# 2. Natural cubic spline basis and REML meta-regression with full covariance
# ---------------------------------------------------------------------------

def ns_basis(x, knots):
    """Natural cubic spline basis (Hastie & Tibshirani parametrisation), no intercept."""
    x = np.asarray(x, float)
    k = np.asarray(knots, float)
    K = len(k)

    def d(j):
        return (np.clip(x - k[j], 0, None) ** 3 - np.clip(x - k[K - 1], 0, None) ** 3) / (k[K - 1] - k[j])
    cols = [x]
    for j in range(K - 2):
        cols.append(d(j) - d(K - 2))
    return np.column_stack(cols)


def reml_metareg(y, v, X):
    y, v = np.asarray(y, float), np.asarray(v, float)
    Xd = np.column_stack([np.ones(len(y)), X])

    def fit(t2):
        W = 1 / (v + t2)
        XtWX = Xd.T @ (Xd * W[:, None])
        beta = np.linalg.solve(XtWX, Xd.T @ (W * y))
        return beta, XtWX, W

    def nll(t2):
        beta, XtWX, W = fit(t2)
        r = y - Xd @ beta
        return 0.5 * (np.sum(np.log(v + t2)) + np.linalg.slogdet(XtWX)[1] + np.sum(W * r * r))

    ub = max(10 * np.var(y), 1e-4)
    res = minimize_scalar(nll, bounds=(0, ub), method="bounded", options={"xatol": 1e-12})
    t2 = float(res.x) if nll(float(res.x)) < nll(0.0) else 0.0
    beta, XtWX, W = fit(t2)
    cov = np.linalg.inv(XtWX)
    df = len(y) - Xd.shape[1]
    r = y - Xd @ beta
    s2 = max(1.0, float(np.sum(W * r * r)) / df) if df > 0 else 1.0
    return dict(beta=beta, cov=cov * s2, tau2=t2, df=df, k=len(y))


def predict(model, Xnew):
    Xd = np.column_stack([np.ones(len(Xnew)), Xnew])
    mu = Xd @ model["beta"]
    se = np.sqrt(np.einsum("ij,jk,ik->i", Xd, model["cov"], Xd))
    return mu, se


# ---------------------------------------------------------------------------
# 3. Build
# ---------------------------------------------------------------------------

def main():
    rows = load_rows()
    rows["usable"] = rows["mean"].notna() & rows["sd"].notna() & rows["n"].notna() & (rows["n"] >= 5) & rows["age"].notna()
    keep_cols = ["kind", "study_id", "first_author", "year", "country", "who_region", "population", "pmid", "doi",
                 "technique", "fatpad_depressed", "stretch", "age_bin_label", "age_lo_years", "age_hi_years", "age",
                 "tanner_system", "tanner_stage", "n", "mean", "sd", "derivation", "source_level", "measurement_concern",
                 "usable", "verbatim_quote"]
    for c in keep_cols:
        if c not in rows:
            rows[c] = np.nan
    rows[keep_cols].to_csv(os.path.join(DATA, "reference_rows.csv"), index=False)

    # ---- age model: age rows + newborn rows; exclude Tanner-only strata and measurement concerns
    A = rows[rows.usable & rows.kind.isin(["newborn", "age", "digitized"]) & ~rows.measurement_concern].copy()
    A = A[(A.age >= 0) & (A.age <= 19)]
    A["t"] = np.log(A.age + 0.25)
    A["y"] = np.log(A["mean"])
    A["v"] = (A["sd"] / A["mean"]) ** 2 / A["n"]
    A["ys"] = np.log(A["sd"]) + 1 / (2 * (A["n"] - 1))
    A["vs"] = 1 / (2 * (A["n"] - 1))
    if A["t"].nunique() >= 6:
        nk = int(np.clip(A["t"].nunique() // 6, 3, 6))
        knots = np.quantile(A["t"].unique(), np.linspace(0.02, 0.98, nk))
        basis = lambda t: ns_basis(t, knots)
    else:  # too little age coverage for a curve: intercept-only (flagged in output)
        knots = np.array([])
        basis = lambda t: np.empty((len(np.atleast_1d(t)), 0))
    B = basis(A["t"])
    mm = reml_metareg(A["y"], A["v"], B)
    ms = reml_metareg(A["ys"], A["vs"], B)
    grid = np.round(np.arange(0, 18.0001, 0.05), 2)
    Bg = basis(np.log(grid + 0.25))
    ly, lse = predict(mm, Bg)
    ls, lsse = predict(ms, Bg)
    tau = math.sqrt(mm["tau2"])
    curve = dict(age=grid.tolist(), mean=np.exp(ly).round(4).tolist(),
                 mean_ci_lo=np.exp(ly - 1.96 * lse).round(4).tolist(), mean_ci_hi=np.exp(ly + 1.96 * lse).round(4).tolist(),
                 pop_mean_pi_lo=np.exp(ly - 1.96 * np.sqrt(tau ** 2 + lse ** 2)).round(4).tolist(),
                 pop_mean_pi_hi=np.exp(ly + 1.96 * np.sqrt(tau ** 2 + lse ** 2)).round(4).tolist(),
                 sd=np.exp(ls).round(4).tolist())
    age_model = dict(k_rows=int(len(A)), k_studies=int(A.study_id.nunique()), n_total=int(A.n.sum()),
                     tau_log=tau, tau2_sd_model=ms["tau2"], knots_t=knots.tolist(),
                     transform="t = ln(age_years + 0.25)", curve=curve)

    # ---- Tanner model
    T = rows[rows.usable & rows.tanner_stage.notna()].copy()
    if "tanner_system" in T:
        ts = T.tanner_system.fillna("").astype(str)
        g = T[ts.str.contains("G|genital", case=False) | ts.eq("") | ts.eq("nan")]
        T = g if len(g) else T
    tanner = {}
    for st in range(1, 6):
        s = T[T.tanner_stage == st]
        if len(s) == 0:
            continue
        y, v = np.log(s["mean"]), (s["sd"] / s["mean"]) ** 2 / s["n"]
        ys, vs = np.log(s["sd"]) + 1 / (2 * (s["n"] - 1)), 1 / (2 * (s["n"] - 1))
        if len(s) >= 2:
            r1 = meta.random_effects(y, v, "REML", hksj=True)
            r2 = meta.random_effects(ys, vs, "REML", hksj=True)
            mu, lo, hi, tau_t = math.exp(r1.mu), math.exp(r1.ci[0]), math.exp(r1.ci[1]), r1.tau
            pil = math.exp(r1.pi[0]) if not math.isnan(r1.pi[0]) else None
            pih = math.exp(r1.pi[1]) if not math.isnan(r1.pi[1]) else None
            sd = math.exp(r2.mu)
        else:
            x = s.iloc[0]
            mu, sd, lo, hi, tau_t, pil, pih = x["mean"], x["sd"], None, None, None, None, None
        tanner[f"G{st}"] = dict(k=int(len(s)), k_studies=int(s.study_id.nunique()), n=int(s.n.sum()), mean=mu,
                                ci_lo=lo, ci_hi=hi, pop_mean_pi_lo=pil, pop_mean_pi_hi=pih, sd=sd, tau_log=tau_t,
                                age_range=[float(np.nanmin(s.age)), float(np.nanmax(s.age))])

    # ---- per-study rows for the lookup table
    P = rows[rows["mean"].notna()].copy()
    P["age_lo"] = P["age_lo_years"].fillna(P["age"] - 0.5)
    P["age_hi"] = P["age_hi_years"].fillna(P["age"] + 0.5)
    studies = []
    for _, r in P.iterrows():
        studies.append(dict(
            study=str(r.get("study_id", "")), author=str(r.get("first_author", "")), year=None if pd.isna(r.get("year")) else int(r["year"]),
            country=str(r.get("country", "")), region=str(r.get("who_region", "")), kind=r["kind"],
            age_label=str(r.get("age_bin_label", "")), age_lo=round(float(r["age_lo"]), 4), age_hi=round(float(r["age_hi"]), 4),
            age_mid=None if pd.isna(r.get("age")) else round(float(r["age"]), 4),
            tanner=None if pd.isna(r.get("tanner_stage")) else int(r["tanner_stage"]),
            n=None if pd.isna(r.get("n")) else int(r["n"]), mean=round(float(r["mean"]), 3),
            sd=None if pd.isna(r["sd"]) else round(float(r["sd"]), 3), derivation=r["derivation"],
            technique=str(r.get("technique", ""))[:160], fatpad=str(r.get("fatpad_depressed", "")),
            source=str(r.get("source_level", "")), concern=bool(r.get("measurement_concern", False)),
            pmid=str(r.get("pmid", "")), doi=str(r.get("doi", ""))))
    model = dict(version=pd.Timestamp.today().strftime("%Y-%m-%d"), age_model=age_model, tanner_model=tanner, rows=studies)
    with open(os.path.join(APP, "model.json"), "w") as f:
        json.dump(model, f, default=lambda x: None if (isinstance(x, float) and math.isnan(x)) else float(x))

    # ---- diagnostic plot
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8, 5))
    m, sd = np.array(curve["mean"]), np.array(curve["sd"])
    ax.fill_between(grid, curve["pop_mean_pi_lo"], curve["pop_mean_pi_hi"], color="#e9e8e4", label="95% PI of a population mean")
    for z, ls_ in ((-2.5, ":"), (2.5, ":")):
        ax.plot(grid, m + z * sd, color="#b03a2e", ls=ls_, lw=1)
    ax.plot(grid, m, color="#1c5cab", lw=2, label="Pooled mean")
    ax.scatter(A.age, A["mean"], s=8 + A.n / 40, color="#2a78d6", alpha=0.6, edgecolor="white", linewidth=0.4, label="Study age-bin means")
    ax.set_xlabel("Age (years)"); ax.set_ylabel("Stretched penile length (cm)")
    ax.spines[["top", "right"]].set_visible(False); ax.legend(frameon=False, fontsize=8)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "pooled_curve.png"), dpi=200); plt.close(fig)
    print(json.dumps(dict(age_rows=len(A), age_studies=age_model["k_studies"], n=age_model["n_total"], tau_log=round(tau, 3),
                          knots=len(knots), tanner={k: (v["k"], round(v["mean"], 2), round(v["sd"], 2)) for k, v in tanner.items()},
                          lookup_rows=len(studies)), indent=1))


if __name__ == "__main__":
    main()
