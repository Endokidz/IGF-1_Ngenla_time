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
    lo2, hi2 = r.get("minus2sd_cm"), r.get("plus2sd_cm")
    if pd.notna(mean) and pd.notna(lo2) and pd.notna(hi2) and hi2 > lo2:
        return mean, (hi2 - lo2) / 4, "SD from reported mean \u00b1 2 SD limits"
    # symmetric percentile pairs (widest available)
    for p in (3, 5, 10, 25):
        lo, hi = r.get(f"p{p}_cm"), r.get(f"p{100 - p}_cm")
        if pd.notna(lo) and pd.notna(hi) and hi > lo:
            med = r.get("p50_cm") if pd.notna(r.get("p50_cm")) else r.get("median_cm")
            m = mean if pd.notna(mean) else (med if pd.notna(med) else (lo + hi) / 2)
            return m, (hi - lo) / (2 * ZP[p]), f"SD from P{p}-P{100 - p} (normal)"
    if pd.notna(r.get("zline_sd")) and pd.notna(r.get("lms_M")):
        return r["lms_M"], r["zline_sd"], "LMS fitted to published -2..+2 SD lines (median M; SD from -1/+1 lines)"
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


ZLINE = re.compile(r"z-scores\s*-2/-1/0/\+1/\+2\s*=\s*([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+)")
RAWN = re.compile(r"raw age-group n for [^=]*=\s*(\d+)")


def lms_fit(z, y):
    """Least-squares LMS (L, M, S) from values y at z-scores z: z = ((y/M)^L - 1)/(L S)."""
    from scipy.optimize import least_squares
    z, y = np.asarray(z, float), np.asarray(y, float)

    def resid(p):
        L, M, S = p
        if abs(L) < 1e-6:
            return np.log(y / M) / S - z
        return ((y / M) ** L - 1) / (L * S) - z
    M0 = y[len(y) // 2]
    S0 = (np.log(y[-1]) - np.log(y[0])) / (z[-1] - z[0])
    r = least_squares(resid, x0=[0.0 + 1e-3, M0, S0], bounds=([-5, 0.1, 1e-3], [5, 50, 2]))
    return r.x, float(np.max(np.abs(r.fun)))


def fit_lms_from_zlines(rows):
    if "notes" not in rows:
        return rows
    for i, r in rows.iterrows():
        m = ZLINE.search(str(r.get("notes", "")))
        if not m:
            continue
        y = [float(v) for v in m.groups()]
        (L, M, S), maxres = lms_fit([-2, -1, 0, 1, 2], y)
        rows.at[i, "lms_L"], rows.at[i, "lms_M"], rows.at[i, "lms_S"] = L, M, S
        rows.at[i, "lms_maxres_z"] = maxres
        rows.at[i, "zline_sd"] = (y[3] - y[1]) / 2          # central SD for pooling on the normal scale
        rows.at[i, "p50_cm"] = y[2]
        nm = RAWN.search(str(r.get("notes", "")))
        if nm and pd.isna(r.get("n")):
            rows.at[i, "n"] = float(nm.group(1))
            rows.at[i, "n_note"] = "raw age-group n (values are LMS-smoothed)"
    return rows


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
           "age_mean_years", "tanner_stage", "year", "minus2sd_cm", "plus2sd_cm"]


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
    rows = fit_lms_from_zlines(rows)
    out = []
    for _, r in rows.iterrows():
        m, s, how = to_mean_sd(r)
        out.append(dict(mean=m, sd=s, derivation=how, age=age_mid(r)))
    rows = pd.concat([rows.reset_index(drop=True), pd.DataFrame(out)], axis=1)
    cur_p = os.path.join(DATA, "tool_curation.csv")
    if os.path.exists(cur_p):
        cur = pd.read_csv(cur_p, dtype=str).fillna("")
        rows["curation_note"] = ""
        drop = np.zeros(len(rows), bool)
        for _, c in cur.iterrows():
            m = (rows.study_id == c.study_id).to_numpy().copy()
            if c.label_contains:
                m &= rows.age_bin_label.fillna("").astype(str).str.contains(c.label_contains, regex=False).to_numpy()
            if c.action == "exclude":
                drop |= m
            elif c.action == "flag":
                rows.loc[m, "measurement_concern"] = True
                rows.loc[m, "curation_note"] = c.reason
        rows = rows[~drop].copy()
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
# 3. Pubertal-stage references
# ---------------------------------------------------------------------------

# Each staging system is a different scale and is pooled separately. Soydan 2012's "genital stage" is a
# testis-volume class, so it is its own system (TV), not Marshall-Tanner G.
STAGE_SYSTEMS = {
    "G": dict(label="Tanner genital stage", prefix="G"),
    "PH": dict(label="Tanner pubic-hair stage", prefix="PH"),
    "TV": dict(label="Testis-volume class (Prader orchidometer, larger testis)", prefix="TV class ",
               classes_ml=[[None, 4.0], [4.0, 12.0], [12.0, 20.0], [20.0, None]],
               class_labels=["1-3.9 mL", "4-11.9 mL", "12-20 mL", ">20 mL"]),
}


def stage_system_of(r):
    if pd.isna(r.get("tanner_stage")):
        return None
    ts = str(r.get("tanner_system", "") or "").strip()
    if re.search(r"testis-volume class", ts, re.I):
        return "TV"
    if re.match(r"(?:genital|G\b)", ts, re.I):
        return "G"
    if re.match(r"pubic hair", ts, re.I):
        return "PH"
    return "unknown"


def pool_stage(s):
    """Pool one stage within one staging system (flagged rows already removed)."""
    base = dict(k=int(len(s)), k_studies=int(s.study_id.nunique()), studies=sorted(s.study_id.unique().tolist()),
                age_range=[float(np.nanmin(s.age)), float(np.nanmax(s.age))] if s.age.notna().any() else None)
    if not s["n"].notna().all():
        # Provisional: equal weights. With the between-study differences seen here (log-scale tau^2 >> v_i),
        # random-effects weights would be close to equal anyway; the study range replaces a prediction interval.
        return base | dict(n=None if s["n"].isna().all() else int(s["n"].sum()), provisional=True,
                           mean=float(np.exp(np.log(s["mean"]).mean())), sd=float(np.exp(np.log(s["sd"]).mean())),
                           ci_lo=None, ci_hi=None, tau_log=None,
                           pop_mean_pi_lo=float(s["mean"].min()) if len(s) > 1 else None,
                           pop_mean_pi_hi=float(s["mean"].max()) if len(s) > 1 else None)
    if len(s) == 1:
        x = s.iloc[0]
        return base | dict(n=int(x["n"]), provisional=False, mean=float(x["mean"]), sd=float(x["sd"]), ci_lo=None, ci_hi=None,
                           pop_mean_pi_lo=None, pop_mean_pi_hi=None, tau_log=None)
    y, v = np.log(s["mean"]), (s["sd"] / s["mean"]) ** 2 / s["n"]
    ys, vs = np.log(s["sd"]) + 1 / (2 * (s["n"] - 1)), 1 / (2 * (s["n"] - 1))
    r1 = meta.random_effects(y, v, "REML", hksj=True)
    r2 = meta.random_effects(ys, vs, "REML", hksj=True)
    pil = math.exp(r1.pi[0]) if not math.isnan(r1.pi[0]) else None
    pih = math.exp(r1.pi[1]) if not math.isnan(r1.pi[1]) else None
    return base | dict(n=int(s.n.sum()), provisional=False, mean=math.exp(r1.mu), sd=math.exp(r2.mu),
                       ci_lo=math.exp(r1.ci[0]), ci_hi=math.exp(r1.ci[1]), pop_mean_pi_lo=pil, pop_mean_pi_hi=pih, tau_log=r1.tau)


def curation_summary(rows):
    """Counts the app quotes in its methods text, computed from the data (never hard-coded)."""
    A = rows[rows.usable & rows.kind.isin(["newborn", "age", "digitized"]) & (rows.age >= 0) & (rows.age <= 19)]
    shown = A[A.measurement_concern]
    return dict(n_rows_lookup=int(rows["mean"].notna().sum()), studies_flagged=sorted(shown.study_id.unique().tolist()),
                n_flagged_rows=int(len(shown)))


# ---------------------------------------------------------------------------
# 4. Build
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
    # SD model: simpler basis (3 knots) - SDs are noisier and sparser than means
    if len(knots) >= 3:
        knots_sd = np.quantile(A["t"].unique(), [0.05, 0.5, 0.95])
        basis_sd = lambda t: ns_basis(t, knots_sd)
    else:
        knots_sd, basis_sd = knots, basis
    ms = reml_metareg(A["ys"], A["vs"], basis_sd(A["t"]))
    grid = np.round(np.arange(0, 18.0001, 0.05), 2)
    Bg = basis(np.log(grid + 0.25))
    ly, lse = predict(mm, Bg)
    ls, lsse = predict(ms, basis_sd(np.log(grid + 0.25)))
    tau = math.sqrt(mm["tau2"])
    curve = dict(age=grid.tolist(), mean=np.exp(ly).round(4).tolist(),
                 mean_ci_lo=np.exp(ly - 1.96 * lse).round(4).tolist(), mean_ci_hi=np.exp(ly + 1.96 * lse).round(4).tolist(),
                 pop_mean_pi_lo=np.exp(ly - 1.96 * np.sqrt(tau ** 2 + lse ** 2)).round(4).tolist(),
                 pop_mean_pi_hi=np.exp(ly + 1.96 * np.sqrt(tau ** 2 + lse ** 2)).round(4).tolist(),
                 sd=np.exp(ls).round(4).tolist(),
                 k_local=[int(A.loc[(A.age >= a - max(0.1, min(1.5, 0.25 * a))) & (A.age <= a + max(0.1, min(1.5, 0.25 * a))),
                                    "study_id"].nunique()) for a in grid])
    age_model = dict(k_rows=int(len(A)), k_studies=int(A.study_id.nunique()), n_total=int(A.n.sum()),
                     tau_log=tau, tau2_sd_model=ms["tau2"], knots_t=knots.tolist(),
                     transform="t = ln(age_years + 0.25)", curve=curve)

    # ---- Pubertal-stage models, one per staging system (never pooled across systems)
    rows["stage_system"] = rows.apply(stage_system_of, axis=1)
    stage_model = {}
    for sysk, spec in STAGE_SYSTEMS.items():
        S = rows[(rows.stage_system == sysk) & rows["mean"].notna() & rows["sd"].notna() & rows.tanner_stage.notna()]
        stages = {}
        for st in sorted(S.tanner_stage.dropna().unique().astype(int)):
            s_all = S[S.tanner_stage == st]
            s = s_all[~s_all.measurement_concern]           # same rule as the age model: flagged rows are shown, not pooled
            shown_only = sorted(s_all.loc[s_all.measurement_concern, "study_id"].unique().tolist())
            if len(s) == 0:
                stages[str(st)] = dict(k=0, k_studies=0, n=None, mean=None, sd=None, studies=[], shown_only=shown_only)
                continue
            stages[str(st)] = pool_stage(s) | dict(shown_only=shown_only)
        stage_model[sysk] = dict(spec, stages=stages)

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
            stage_system=None if pd.isna(r.get("tanner_stage")) else r.get("stage_system"),
            n=None if pd.isna(r.get("n")) else int(r["n"]), mean=round(float(r["mean"]), 3),
            sd=None if pd.isna(r["sd"]) else round(float(r["sd"]), 3), derivation=r["derivation"],
            technique=str(r.get("technique", ""))[:160], fatpad=str(r.get("fatpad_depressed", "")),
            source=str(r.get("source_level", "")), concern=bool(r.get("measurement_concern", False)),
            pmid=str(r.get("pmid", "")), doi=str(r.get("doi", "")),
            lms=None if pd.isna(r.get("lms_L")) or pd.isna(r.get("lms_S")) else [round(float(r["lms_L"]), 4), round(float(r["lms_M"]), 4), round(float(r["lms_S"]), 5)],
            note=str(r.get("curation_note", "") or "")))
    model = dict(version=pd.Timestamp.today().strftime("%Y-%m-%d"), age_model=age_model, stage_model=stage_model, rows=studies,
                 curation=curation_summary(rows))
    def clean(o):
        if isinstance(o, dict):
            return {k: clean(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [clean(v) for v in o]
        if isinstance(o, (np.floating, float)):
            return None if not math.isfinite(float(o)) else float(o)
        if isinstance(o, np.integer):
            return int(o)
        if isinstance(o, np.bool_):
            return bool(o)
        return o
    with open(os.path.join(APP, "model.json"), "w") as f:
        json.dump(clean(model), f, allow_nan=False)

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
                          knots=len(knots), stages={f"{sk}{st}": (v["k"], v["mean"] and round(v["mean"], 2), v["sd"] and round(v["sd"], 2),
                                                   "prov" if v.get("provisional") else "")
                                                for sk, sm in stage_model.items() for st, v in sm["stages"].items()},
                          lookup_rows=len(studies)), indent=1))


if __name__ == "__main__":
    main()
