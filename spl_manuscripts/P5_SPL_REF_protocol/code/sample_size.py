"""
P5 — SPL-REF protocol: sample-size and design calculations.

All calculations are analytic and reproducible; each block cites its source.
"""
import json
import math
import os

import numpy as np
from scipy import stats

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
os.makedirs(OUT, exist_ok=True)
res = {}

# ---------------------------------------------------------------------------
# 1. Main cross-sectional reference sample (0-18 y)
#    Cole (Stat Methods Med Res 2021;30:488-507): with n = 6878 boys 0-21 y and
#    GAMLSS smoothing, SE = 0.066 z-units for the 2nd/98th centiles.
#    SE scales with 1/sqrt(n). Relative difficulty of the -2.5 SD centile vs the
#    2nd centile (z = -2.054) from the asymptotic SE of a normal quantile:
#       SE(z_p) ~ sqrt((1 + z_p^2 / 2) / n)
# ---------------------------------------------------------------------------
n_cole, se_cole, z2 = 6878, 0.066, stats.norm.ppf(0.02)
ratio = math.sqrt((1 + 2.5 ** 2 / 2) / (1 + z2 ** 2 / 2))
targets = {}
for se_target in (0.08, 0.10, 0.12):
    n2 = n_cole * (se_cole / se_target) ** 2          # n for this SE at 2nd centile
    n25 = n2 * ratio ** 2                             # n for this SE at -2.5 SD
    targets[se_target] = dict(n_for_2nd_centile=round(n2), n_for_minus2p5SD=round(n25))
res["centile_precision"] = dict(ratio_minus2p5_vs_2nd=ratio, targets=targets)
N_ANALYSABLE = int(math.ceil(targets[0.10]["n_for_minus2p5SD"] / 100.0) * 100)
N_ENROL = int(math.ceil(N_ANALYSABLE / 0.90 / 100.0) * 100)   # 10% exclusion / unusable
res["N_analysable"] = N_ANALYSABLE
res["N_enrol"] = N_ENROL

# Naive (unsmoothed) per-window n for SE 0.10 at -2.5 SD, for comparison
res["naive_per_window_n_SE0.10"] = math.ceil((1 + 2.5 ** 2 / 2) / 0.10 ** 2)

# ---------------------------------------------------------------------------
# 2. Age composition: uniform on age^lambda, lambda = 0.75 (Cole 2021 optimum
#    for the 2nd/98th centiles), age range 0-18 y. Allocate N_ANALYSABLE.
# ---------------------------------------------------------------------------
lam = 0.75
amax = 18.0
bands = [(0, 1 / 12), (1 / 12, 0.5), (0.5, 1), (1, 2), (2, 5), (5, 9), (9, 11), (11, 13), (13, 15), (15, 18)]
labels = ["0-1 mo", "1-6 mo", "6-12 mo", "1-2 y", "2-5 y", "5-9 y", "9-11 y", "11-13 y", "13-15 y", "15-18 y"]
alloc = []
tot = amax ** lam
for (a, b), lab in zip(bands, labels):
    p = (b ** lam - a ** lam) / tot
    alloc.append(dict(band=lab, proportion=p, n=round(p * N_ANALYSABLE)))
res["age_allocation_lambda0.75"] = alloc

# Pubertal over-sampling: the 9-15 y bands carry the largest between-child
# variance (asynchronous gonadarche). Inflate them by 25% and record total.
over = []
for row in alloc:
    f = 1.25 if row["band"] in ("9-11 y", "11-13 y", "13-15 y") else 1.0
    over.append(dict(row, n_with_pubertal_oversampling=math.ceil(row["n"] * f)))
res["age_allocation_with_pubertal_oversampling"] = over
res["N_analysable_with_oversampling"] = sum(r["n_with_pubertal_oversampling"] for r in over)

# ---------------------------------------------------------------------------
# 3. Neonatal sub-cohort (term, 24-72 h): precision of mean and of -2.5 SD
#    (naive, unsmoothed, single time point).
# ---------------------------------------------------------------------------
sd_newborn_cm = 0.40     # Boas et al. Eur J Endocrinol 2006 (3.49 +/- 0.4 cm at birth)
neo = []
for n in (500, 750, 1000, 1500):
    se_mean = sd_newborn_cm / math.sqrt(n)
    se_q = sd_newborn_cm * math.sqrt((1 + 2.5 ** 2 / 2) / n)
    neo.append(dict(n=n, se_mean_cm=se_mean, ci95_halfwidth_mean_cm=1.96 * se_mean,
                    se_minus2p5SD_cm=se_q, ci95_halfwidth_minus2p5SD_cm=1.96 * se_q))
res["neonatal_precision"] = neo

# ---------------------------------------------------------------------------
# 4. Nested minipuberty cohort: correlation between serum testosterone at
#    2-3 months and SPL velocity 0-3 months. Boas 2006 reported r = 0.31 for
#    attained length; we power for a conservative r = 0.25.
#    Fisher z: n = ((z_a/2 + z_b) / atanh(r))^2 + 3
# ---------------------------------------------------------------------------
def n_corr(r, alpha=0.05, power=0.80):
    za, zb = stats.norm.ppf(1 - alpha / 2), stats.norm.ppf(power)
    return math.ceil(((za + zb) / math.atanh(r)) ** 2 + 3)

mp = {f"r={r}_power={p}": n_corr(r, power=p) for r in (0.20, 0.25, 0.30) for p in (0.80, 0.90)}
n_mp = n_corr(0.25, power=0.80)
res["minipuberty_corr"] = mp
res["minipuberty_n_enrol_20pct_attrition"] = math.ceil(n_mp / 0.80)

# ---------------------------------------------------------------------------
# 5. Reliability sub-study: ICC(2,1) precision (Bonett, Stat Med 2002):
#    n = 1 + 8 z^2 (1-rho)^2 (1+(k-1) rho)^2 / (k (k-1) w^2), w = full CI width
#    and Walter, Eliasziw & Donner (Stat Med 1998) hypothesis-testing design.
# ---------------------------------------------------------------------------
def n_bonett(rho, k, w, alpha=0.05):
    z = stats.norm.ppf(1 - alpha / 2)
    return math.ceil(1 + 8 * z ** 2 * (1 - rho) ** 2 * (1 + (k - 1) * rho) ** 2 / (k * (k - 1) * w ** 2))

def n_walter(rho0, rho1, k, alpha=0.05, power=0.80):
    za, zb = stats.norm.ppf(1 - alpha), stats.norm.ppf(power)   # one-sided
    c0 = (1 + k * rho0 / (1 - rho0)) / (1 + k * rho1 / (1 - rho1))
    return math.ceil(1 + 2 * (za + zb) ** 2 * k / ((math.log(c0)) ** 2 * (k - 1)))

rel = {
    "bonett_rho=0.80_k=3_w=0.10": n_bonett(0.80, 3, 0.10),
    "bonett_rho=0.90_k=3_w=0.10": n_bonett(0.90, 3, 0.10),
    "bonett_rho=0.90_k=3_w=0.08": n_bonett(0.90, 3, 0.08),
    "walter_rho0=0.75_rho1=0.90_k=3": n_walter(0.75, 0.90, 3),
    "walter_rho0=0.80_rho1=0.90_k=3": n_walter(0.80, 0.90, 3),
}
res["reliability_icc"] = rel

# Precision of the within-subject (error) SD: with n subjects x k raters,
# df = n (k - 1); 95% CI for SD_e is SD_e * sqrt(df / chi2).
def sd_ci_ratio(n, k):
    df = n * (k - 1)
    lo = math.sqrt(df / stats.chi2.ppf(0.975, df))
    hi = math.sqrt(df / stats.chi2.ppf(0.025, df))
    return lo, hi
res["error_sd_ci_multipliers"] = {f"n={n}_k=3": sd_ci_ratio(n, 3) for n in (30, 60, 100, 240)}

# Bland-Altman: approximate 95% CI half-width of a limit of agreement =
# 1.96 * sqrt(3 / n) * s_diff (Bland & Altman, Lancet 1986)
res["LoA_ci_halfwidth_in_sdiff_units"] = {n: 1.96 * math.sqrt(3 / n) for n in (30, 60, 100, 240)}

# ---------------------------------------------------------------------------
# 6. Fat-pad sub-study: paired difference (fat pad depressed - not depressed)
#    regressed on BMI-SDS. Power to detect slope beta with residual SD s_r and
#    SD of BMI-SDS s_x: n = ((z_a/2 + z_b) * s_r / (beta * s_x))^2 + 2
#    Assumptions stated in the protocol; illustrated for a grid.
# ---------------------------------------------------------------------------
def n_slope(beta, s_r, s_x, alpha=0.05, power=0.90):
    za, zb = stats.norm.ppf(1 - alpha / 2), stats.norm.ppf(power)
    return math.ceil(((za + zb) * s_r / (beta * s_x)) ** 2 + 2)

fp = {}
for beta in (0.10, 0.15, 0.20):
    for s_r in (0.40, 0.60):
        fp[f"beta={beta}cm_per_BMI-SDS_sr={s_r}cm"] = n_slope(beta, s_r, 1.2)
res["fat_pad_slope_n_(s_x=1.2_power0.90)"] = fp

with open(os.path.join(OUT, "sample_size_results.json"), "w") as f:
    json.dump(res, f, indent=2, default=float)
print(json.dumps(res, indent=1, default=lambda x: round(float(x), 4)))
