"""
P4 — Monte Carlo study of micropenis misclassification under the -2.5 SD rule.

ADEMP structure (Morris, White & Crowther, Stat Med 2019):

Aims
  Quantify how random measurement error (within- and between-observer),
  systematic technique bias (e.g. failure to depress the suprapubic fat pad,
  sub-maximal stretch) and reference-population mismatch distort the apparent
  prevalence and diagnostic accuracy of the "SPL < mean - 2.5 SD" criterion,
  and evaluate mitigation strategies (replicate measurement, second observer,
  two-stage confirmation, population-appropriate references).

Data-generating mechanism (all in SD units of the TRUE population distribution)
  z_true_i            ~ N(0, 1)   [sensitivity: skew-normal, standardised]
  b_j (observer)      ~ N(0, lam_b^2)        between-observer systematic error
  e_ijr (replicate)   ~ N(0, lam_w^2)        within-observer error
  d_i (technique)     ~ N(delta, sd_delta^2) child-specific technique bias
  z_obs_ijr = z_true_i + d_i + b_j + e_ijr - shift_ref
  where lam^2 = lam_b^2 + lam_w^2 and phi = lam_b^2 / lam^2.
  Reference mismatch: the clinician standardises against a reference whose
  mean differs from the true population mean by `shift_ref` (in true-SD units)
  and whose SD is `scale_ref` times the true SD.

Estimands
  Apparent prevalence P(test+), true prevalence P(z_true < -2.5),
  sensitivity, specificity, PPV, NPV, false positives per 10 000 boys,
  inflation ratio = apparent / true prevalence.

Methods (diagnostic strategies)
  S1 single measurement
  S2 mean of two replicates, same observer
  S3 mean of two measurements, two independent observers
  S4 two-stage: second independent observer only if first is positive;
     positive if the mean of both is below the cut-off
  S5 two-stage, both-positive rule (each of two independent observers < cut-off)

Performance
  Monte Carlo standard errors are reported for every estimand; S1 is checked
  against closed-form bivariate-normal results.
"""
from __future__ import annotations

import itertools
import json
import math
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "data")
FIG = os.path.join(HERE, "..", "figures")
CUT = -2.5
N_SIM = 4_000_000          # simulated boys per scenario
SEED = 20261118


# ---------------------------------------------------------------------------
# Analytic results for strategy S1 (normal model) — used for validation
# ---------------------------------------------------------------------------

def analytic_s1(lam, delta=0.0, sd_delta=0.0, shift_ref=0.0, scale_ref=1.0, cut=CUT):
    """Closed-form accuracy for a single measurement under the normal model.

    Test positive if (z_obs_raw - shift_ref)/scale_ref < cut, where
    z_obs_raw = z + d + error.  Equivalent to z + d + err < cut*scale_ref + shift_ref.
    """
    c_obs = cut * scale_ref + shift_ref
    s_obs = math.sqrt(1 + lam ** 2 + sd_delta ** 2)
    p_true = stats.norm.cdf(cut)
    p_pos = stats.norm.cdf((c_obs - delta) / s_obs)
    # P(z < cut, z + d + err < c_obs) by 1-D quadrature over z (exact to ~1e-12;
    # avoids the singular covariance at lam = 0 and the limited tail precision
    # of generic bivariate-normal CDF routines).
    s_err = math.sqrt(lam ** 2 + sd_delta ** 2)
    if s_err == 0:
        p_tp = stats.norm.cdf(min(cut, c_obs - delta))
    else:
        from scipy.integrate import quad
        f = lambda z: stats.norm.pdf(z) * stats.norm.cdf((c_obs - delta - z) / s_err)
        p_tp = quad(f, -12, cut, epsabs=1e-14, epsrel=1e-10, limit=200)[0]
    sens = p_tp / p_true
    spec = (1 - p_pos - (p_true - p_tp)) / (1 - p_true)
    ppv = p_tp / p_pos if p_pos > 0 else float("nan")
    npv = (1 - p_pos - (p_true - p_tp)) / (1 - p_pos)
    return dict(p_true=p_true, p_pos=p_pos, sens=sens, spec=spec, ppv=ppv, npv=npv,
                fp_per_10k=1e4 * (p_pos - p_tp), inflation=p_pos / p_true)


# ---------------------------------------------------------------------------
# Monte Carlo
# ---------------------------------------------------------------------------

def draw_true(rng, n, skew_alpha=0.0):
    if skew_alpha == 0.0:
        return rng.standard_normal(n)
    sn = stats.skewnorm(skew_alpha)
    m, v = sn.stats(moments="mv")
    x = sn.rvs(size=n, random_state=rng)
    return (x - m) / math.sqrt(v)


def simulate(lam, phi=0.5, delta=0.0, sd_delta=0.0, shift_ref=0.0, scale_ref=1.0,
             skew_alpha=0.0, n=N_SIM, seed=SEED, cut=CUT):
    rng = np.random.default_rng(seed)
    lam_b = math.sqrt(phi) * lam
    lam_w = math.sqrt(1 - phi) * lam
    z = draw_true(rng, n, skew_alpha)
    d = delta + sd_delta * rng.standard_normal(n)       # child-specific technique bias
    # Two observers per child (observer effects drawn per child-observer encounter;
    # equivalent to a large pool of observers each seeing few children).
    b1 = lam_b * rng.standard_normal(n)
    b2 = lam_b * rng.standard_normal(n)
    e11 = lam_w * rng.standard_normal(n)   # observer 1, replicate 1
    e12 = lam_w * rng.standard_normal(n)   # observer 1, replicate 2
    e21 = lam_w * rng.standard_normal(n)   # observer 2, replicate 1
    # NB: technique bias d is shared across observers (same flawed technique);
    # a separate scenario examines an observer-specific technique error below.
    std = lambda raw: (raw - shift_ref) / scale_ref
    o11 = std(z + d + b1 + e11)
    o12 = std(z + d + b1 + e12)
    o21 = std(z + d + b2 + e21)
    truth = z < cut
    tests = {
        "S1_single": o11 < cut,
        "S2_mean2_same_observer": (o11 + o12) / 2 < cut,
        "S3_mean2_two_observers": (o11 + o21) / 2 < cut,
        "S4_two_stage_mean": (o11 < cut) & ((o11 + o21) / 2 < cut),
        "S5_two_stage_both": (o11 < cut) & (o21 < cut),
    }
    rows = []
    n_true = truth.sum()
    # Regression to the mean among boys flagged by a single measurement:
    # apparent 'growth' on an untreated re-measurement (SD units).
    flag = o11 < cut
    rtm_other = float(np.mean(o21[flag] - o11[flag])) if flag.any() else float("nan")
    rtm_same = float(np.mean(o12[flag] - o11[flag])) if flag.any() else float("nan")
    rtm_other_sd = float(np.std(o21[flag] - o11[flag], ddof=1)) if flag.sum() > 1 else float("nan")
    for name, pos in tests.items():
        tp = np.sum(pos & truth)
        fp = np.sum(pos & ~truth)
        fn = np.sum(~pos & truth)
        tn = n - tp - fp - fn
        npos = tp + fp
        p_pos = npos / n
        sens = tp / n_true
        spec = tn / (n - n_true)
        ppv = tp / npos if npos else float("nan")
        npv = tn / (tn + fn)
        rows.append(dict(
            strategy=name, lam=lam, phi=phi, delta=delta, sd_delta=sd_delta,
            shift_ref=shift_ref, scale_ref=scale_ref, skew_alpha=skew_alpha, n=n,
            p_true=n_true / n, p_pos=p_pos,
            p_pos_mcse=math.sqrt(p_pos * (1 - p_pos) / n),
            sens=sens, sens_mcse=math.sqrt(sens * (1 - sens) / n_true),
            spec=spec, ppv=ppv,
            ppv_mcse=math.sqrt(ppv * (1 - ppv) / npos) if npos else float("nan"),
            npv=npv, fp_per_10k=1e4 * fp / n,
            inflation=p_pos / (n_true / n),
            rtm_remeasure_other_observer=rtm_other, rtm_remeasure_same_observer=rtm_same,
            rtm_sd_other_observer=rtm_other_sd,
            second_measurements_per_10k=(1e4 * np.mean(o11 < cut)) if name.startswith("S4") or name.startswith("S5")
            else (1e4 if name in ("S2_mean2_same_observer", "S3_mean2_two_observers") else 0.0),
        ))
    return rows


def main():
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(FIG, exist_ok=True)
    grid_lam = [0.0, 0.1, 0.25, 0.5, 0.75, 1.0]
    grid_delta = [0.0, -0.25, -0.5, -1.0]
    rows = []
    seed = SEED
    # --- Experiment A: random error x technique bias (fully factorial) --------
    for lam, delta in itertools.product(grid_lam, grid_delta):
        seed += 1
        rows += [dict(r, experiment="A_error_x_bias") for r in simulate(lam, 0.5, delta, seed=seed)]
    # --- Experiment B: heterogeneous technique bias (fat pad varies by child) -
    for lam, (delta, sdd) in itertools.product([0.25, 0.5], [(-0.5, 0.25), (-0.5, 0.5), (-1.0, 0.5)]):
        seed += 1
        rows += [dict(r, experiment="B_heterogeneous_bias") for r in simulate(lam, 0.5, delta, sdd, seed=seed)]
    # --- Experiment C: share of error that is between-observer ---------------
    for lam, phi in itertools.product([0.25, 0.5, 0.75], [0.0, 0.5, 0.8]):
        seed += 1
        rows += [dict(r, experiment="C_observer_share") for r in simulate(lam, phi, seed=seed)]
    # --- Experiment D: reference mismatch -----------------------------------
    for shift, scale in itertools.product([-1.0, -0.5, 0.0, 0.5, 1.0], [0.8, 1.0, 1.25]):
        seed += 1
        rows += [dict(r, experiment="D_reference_mismatch") for r in simulate(0.25, 0.5, 0.0, 0.0, shift, scale, seed=seed)]
    # --- Experiment E: non-normal (skewed) true distribution ----------------
    for lam, alpha in itertools.product([0.0, 0.25, 0.5], [-3.0, -1.5, 0.0, 1.5, 3.0]):
        seed += 1
        rows += [dict(r, experiment="E_skewness") for r in simulate(lam, 0.5, skew_alpha=alpha, seed=seed)]
    # --- Experiment F: reference built with the SAME measurement error -----
    # Reference SD = sqrt(1 + lam^2) (error-inflated), reference mean unbiased.
    for lam in [0.25, 0.5, 0.75, 1.0]:
        seed += 1
        rows += [dict(r, experiment="F_matched_error_reference")
                 for r in simulate(lam, 0.5, 0.0, 0.0, 0.0, math.sqrt(1 + lam ** 2), seed=seed)]
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, "simulation_results.csv"), index=False)

    # --- Validation of S1 against closed form ---------------------------------
    val = []
    for _, r in df[df.strategy == "S1_single"].iterrows():
        if r.skew_alpha != 0:
            continue
        a = analytic_s1(r.lam, r.delta, r.sd_delta, r.shift_ref, r.scale_ref)
        val.append(dict(experiment=r.experiment, lam=r.lam, delta=r.delta, sd_delta=r.sd_delta,
                        shift_ref=r.shift_ref, scale_ref=r.scale_ref,
                        mc_p_pos=r.p_pos, an_p_pos=a["p_pos"], z_p_pos=(r.p_pos - a["p_pos"]) / r.p_pos_mcse,
                        mc_ppv=r.ppv, an_ppv=a["ppv"],
                        mc_sens=r.sens, an_sens=a["sens"]))
    vdf = pd.DataFrame(val)
    vdf.to_csv(os.path.join(OUT, "validation_s1_vs_analytic.csv"), index=False)
    print("Validation: max |z| for apparent prevalence =", round(vdf.z_p_pos.abs().max(), 2),
          "; max |PPV diff| =", round((vdf.mc_ppv - vdf.an_ppv).abs().max(), 4))

    # --- Analytic fine grid for figures --------------------------------------
    fine = []
    for lam in np.round(np.arange(0, 1.0001, 0.02), 3):
        for delta in grid_delta:
            a = analytic_s1(lam, delta)
            fine.append(dict(lam=lam, delta=delta, **a))
    fdf = pd.DataFrame(fine)
    fdf.to_csv(os.path.join(OUT, "analytic_grid_s1.csv"), index=False)

    # --- Replicates needed to keep PPV >= target (analytic, mean of m by
    #     independent observers, delta = 0) --------------------------------------
    req = []
    for lam in [0.1, 0.25, 0.5, 0.75, 1.0]:
        for target in [0.5, 0.67, 0.8]:
            m_need = None
            for m in range(1, 51):
                if analytic_s1(lam / math.sqrt(m))["ppv"] >= target:
                    m_need = m
                    break
            req.append(dict(lam=lam, ppv_target=target, m_independent_measurements=m_need))
    pd.DataFrame(req).to_csv(os.path.join(OUT, "replicates_needed.csv"), index=False)

    meta = dict(N_SIM=N_SIM, SEED=SEED, CUT=CUT, n_scenarios=int(len(df) / 5),
                numpy=np.__version__, scipy=__import__("scipy").__version__, pandas=pd.__version__)
    with open(os.path.join(OUT, "run_metadata.json"), "w") as f:
        json.dump(meta, f, indent=2)
    print(json.dumps(meta))


if __name__ == "__main__":
    main()
