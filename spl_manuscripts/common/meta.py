"""
Shared meta-analysis utilities for the SPL manuscript series.

Implements (all formulas from the cited methodological literature):
  * Random-effects meta-analysis: DerSimonian-Laird and REML (Fisher scoring)
  * Hartung-Knapp-Sidik-Jonkman (HKSJ) small-sample adjustment
  * Prediction interval (Higgins, Thompson & Spiegelhalter 2009; Riley 2011)
  * I^2, H^2, Cochran's Q
  * Egger's regression test for small-study effects
  * Mixed-effects meta-regression (REML tau^2, HKSJ-type t-tests)
  * Estimation of mean/SD from median, quartiles, range
    (Luo et al. 2018 for means; Wan et al. 2014 for SDs)
  * Pre-post change SD from arm-level SDs and an assumed/imputed correlation

No external meta-analysis package is required; numpy/scipy only.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional, Sequence

import numpy as np
from scipy import stats


# ---------------------------------------------------------------------------
# Summary-statistic conversions
# ---------------------------------------------------------------------------

def _xi(n: float) -> float:
    """Wan et al. 2014: expected range of n standard normal draws (approx.)."""
    return 2.0 * stats.norm.ppf((n - 0.375) / (n + 0.25))


def _eta(n: float) -> float:
    """Wan et al. 2014: expected IQR of n standard normal draws (approx.)."""
    return 2.0 * stats.norm.ppf((0.75 * n - 0.125) / (n + 0.25))


def mean_sd_from_summary(n, median=None, q1=None, q3=None, mn=None, mx=None):
    """Return (mean, sd, method) estimated from reported quantiles.

    Scenario S1: min, median, max      -> Luo (2018) mean, Wan (2014) SD
    Scenario S2: q1, median, q3        -> Luo (2018) mean, Wan (2014) SD
    Scenario S3: min, q1, median, q3, max -> Luo (2018) mean, Wan (2014) SD
    """
    n = float(n)
    have = lambda *xs: all(x is not None and not (isinstance(x, float) and math.isnan(x)) for x in xs)
    if have(mn, q1, median, q3, mx):
        w1 = 2.2 / (2.2 + n ** 0.75)
        w2 = 0.7 - 0.72 / n ** 0.55
        mean = w1 * (mn + mx) / 2 + w2 * (q1 + q3) / 2 + (1 - w1 - w2) * median
        sd = (mx - mn) / (2 * _xi(n)) + (q3 - q1) / (2 * _eta(n))
        return mean, sd, "S3_Luo2018_Wan2014"
    if have(q1, median, q3):
        w = 0.7 + 0.39 / n
        mean = w * (q1 + q3) / 2 + (1 - w) * median
        sd = (q3 - q1) / _eta(n)
        return mean, sd, "S2_Luo2018_Wan2014"
    if have(mn, median, mx):
        w = 4.0 / (4.0 + n ** 0.75)
        mean = w * (mn + mx) / 2 + (1 - w) * median
        sd = (mx - mn) / _xi(n)
        return mean, sd, "S1_Luo2018_Wan2014"
    raise ValueError("Insufficient summary statistics")


def change_sd(sd_pre, sd_post, r):
    """SD of within-person change given arm SDs and pre-post correlation r."""
    return math.sqrt(sd_pre ** 2 + sd_post ** 2 - 2 * r * sd_pre * sd_post)


def implied_r(sd_pre, sd_post, sd_change):
    """Back-calculate pre-post correlation (Cochrane Handbook 6.5.2.8)."""
    return (sd_pre ** 2 + sd_post ** 2 - sd_change ** 2) / (2 * sd_pre * sd_post)


# ---------------------------------------------------------------------------
# Random-effects meta-analysis
# ---------------------------------------------------------------------------

@dataclass
class MAResult:
    k: int
    mu: float
    se: float
    ci: tuple
    tau2: float
    tau: float
    Q: float
    Q_p: float
    I2: float
    H2: float
    pi: tuple
    method: str
    hksj: bool
    weights: np.ndarray = field(repr=False)
    tau2_ci: Optional[tuple] = None

    def as_dict(self):
        return {
            "k": self.k, "mu": self.mu, "se": self.se,
            "ci_lo": self.ci[0], "ci_hi": self.ci[1],
            "tau2": self.tau2, "tau": self.tau, "Q": self.Q, "Q_p": self.Q_p,
            "I2": self.I2, "H2": self.H2, "pi_lo": self.pi[0], "pi_hi": self.pi[1],
            "method": self.method, "hksj": self.hksj,
        }


def _tau2_dl(y, v):
    w = 1 / v
    mu_fe = np.sum(w * y) / np.sum(w)
    Q = np.sum(w * (y - mu_fe) ** 2)
    c = np.sum(w) - np.sum(w ** 2) / np.sum(w)
    return max(0.0, (Q - (len(y) - 1)) / c)


def _tau2_reml(y, v, tol=1e-10, maxit=500):
    tau2 = _tau2_dl(y, v)
    for _ in range(maxit):
        w = 1 / (v + tau2)
        mu = np.sum(w * y) / np.sum(w)
        # REML score and Fisher information (Viechtbauer 2005)
        P_diag_term = w - w ** 2 / np.sum(w)
        resid = y - mu
        score = 0.5 * (np.sum(w ** 2 * resid ** 2) - np.sum(P_diag_term))
        info = 0.5 * np.sum(w ** 2) - np.sum(w ** 3) / np.sum(w) + 0.5 * (np.sum(w ** 2) / np.sum(w)) ** 2
        step = score / info
        new = max(0.0, tau2 + step)
        if abs(new - tau2) < tol:
            tau2 = new
            break
        tau2 = new
    return tau2


def _tau2_qprofile_ci(y, v, alpha=0.05):
    """Q-profile CI for tau^2 (Viechtbauer 2007)."""
    k = len(y)

    def gen_q(t2):
        w = 1 / (v + t2)
        mu = np.sum(w * y) / np.sum(w)
        return np.sum(w * (y - mu) ** 2)

    lo_target = stats.chi2.ppf(1 - alpha / 2, k - 1)
    hi_target = stats.chi2.ppf(alpha / 2, k - 1)
    upper_bound = max(10 * np.var(y, ddof=1) + 10 * np.max(v), 1.0)

    def solve(target):
        f = lambda t2: gen_q(t2) - target
        if f(0) < 0:
            return 0.0
        a, b = 0.0, upper_bound
        while f(b) > 0:
            b *= 2
            if b > 1e8:
                return float("inf")
        for _ in range(200):
            m = (a + b) / 2
            if f(m) > 0:
                a = m
            else:
                b = m
        return (a + b) / 2

    return solve(lo_target), solve(hi_target)


def random_effects(y: Sequence[float], v: Sequence[float], method: str = "REML",
                   hksj: bool = True, alpha: float = 0.05) -> MAResult:
    y = np.asarray(y, float)
    v = np.asarray(v, float)
    k = len(y)
    if k < 2:
        raise ValueError("Need >= 2 studies")
    tau2 = _tau2_reml(y, v) if method.upper() == "REML" else _tau2_dl(y, v)
    w = 1 / (v + tau2)
    mu = np.sum(w * y) / np.sum(w)
    se = math.sqrt(1 / np.sum(w))
    # Cochran's Q from fixed-effect weights
    wf = 1 / v
    mu_fe = np.sum(wf * y) / np.sum(wf)
    Q = float(np.sum(wf * (y - mu_fe) ** 2))
    Q_p = float(1 - stats.chi2.cdf(Q, k - 1))
    I2 = max(0.0, (Q - (k - 1)) / Q) if Q > 0 else 0.0
    H2 = Q / (k - 1) if k > 1 else float("nan")
    if hksj:
        q_hk = np.sum(w * (y - mu) ** 2) / (k - 1)
        se_hk = math.sqrt(max(q_hk, 1.0) * se ** 2)  # truncated HKSJ (Knapp-Hartung "ad hoc" variance correction)
        tcrit = stats.t.ppf(1 - alpha / 2, k - 1)
        ci = (mu - tcrit * se_hk, mu + tcrit * se_hk)
        se_out = se_hk
    else:
        z = stats.norm.ppf(1 - alpha / 2)
        ci = (mu - z * se, mu + z * se)
        se_out = se
    if k >= 3:
        tpi = stats.t.ppf(1 - alpha / 2, k - 2)
        half = tpi * math.sqrt(tau2 + se_out ** 2)
        pi = (mu - half, mu + half)
    else:
        pi = (float("nan"), float("nan"))
    try:
        t2ci = _tau2_qprofile_ci(y, v, alpha)
    except Exception:
        t2ci = None
    return MAResult(k, float(mu), float(se_out), ci, float(tau2), math.sqrt(tau2), Q, Q_p,
                    float(I2), float(H2), pi, method.upper(), hksj, w / np.sum(w), t2ci)


def egger_test(y, v):
    """Egger's regression: standardized effect on precision. Returns (intercept, se, t, p)."""
    y = np.asarray(y, float)
    se = np.sqrt(np.asarray(v, float))
    Y = y / se
    X = np.column_stack([np.ones_like(se), 1 / se])
    beta, *_ = np.linalg.lstsq(X, Y, rcond=None)
    resid = Y - X @ beta
    df = len(y) - 2
    s2 = resid @ resid / df
    cov = s2 * np.linalg.inv(X.T @ X)
    b0, se0 = beta[0], math.sqrt(cov[0, 0])
    t = b0 / se0
    p = 2 * (1 - stats.t.cdf(abs(t), df))
    return float(b0), float(se0), float(t), float(p)


def meta_regression(y, v, X, names=None, hksj=True):
    """Mixed-effects meta-regression with REML tau^2 and Knapp-Hartung t-tests.

    X: (k x p) design matrix WITHOUT intercept column; intercept is added.
    Returns dict with coefficients, se, t, p, tau2, R2 (proportion of tau^2 explained).
    """
    y = np.asarray(y, float)
    v = np.asarray(v, float)
    X = np.asarray(X, float)
    if X.ndim == 1:
        X = X[:, None]
    k, p = X.shape
    Xd = np.column_stack([np.ones(k), X])
    pp = Xd.shape[1]

    def fit(t2):
        W = np.diag(1 / (v + t2))
        XtWX = Xd.T @ W @ Xd
        beta = np.linalg.solve(XtWX, Xd.T @ W @ y)
        return beta, XtWX, W

    # REML for residual tau^2 by 1-D optimisation of restricted log-likelihood
    def neg_rll(t2):
        if t2 < 0:
            return 1e20
        beta, XtWX, W = fit(t2)
        r = y - Xd @ beta
        return 0.5 * (np.sum(np.log(v + t2)) + np.log(np.linalg.det(XtWX)) + r @ W @ r)

    from scipy.optimize import minimize_scalar
    ub = max(10 * np.var(y, ddof=1), 1e-6)
    res = minimize_scalar(neg_rll, bounds=(0, ub), method="bounded", options={"xatol": 1e-10})
    t2 = float(res.x)
    if neg_rll(0.0) <= res.fun:
        t2 = 0.0
    beta, XtWX, W = fit(t2)
    cov = np.linalg.inv(XtWX)
    r = y - Xd @ beta
    df = k - pp
    if hksj and df > 0:
        s2 = max(1.0, float(r @ W @ r) / df)
        cov = cov * s2
        se = np.sqrt(np.diag(cov))
        tval = beta / se
        pval = 2 * (1 - stats.t.cdf(np.abs(tval), df))
        crit = stats.t.ppf(0.975, df)
    else:
        se = np.sqrt(np.diag(cov))
        tval = beta / se
        pval = 2 * (1 - stats.norm.cdf(np.abs(tval)))
        crit = 1.959964
    tau2_null = _tau2_reml(y, v)
    R2 = max(0.0, (tau2_null - t2) / tau2_null) if tau2_null > 0 else 0.0
    names = ["intercept"] + (list(names) if names else [f"x{i+1}" for i in range(p)])
    out = {
        "coef": dict(zip(names, beta.tolist())),
        "se": dict(zip(names, se.tolist())),
        "ci_lo": dict(zip(names, (beta - crit * se).tolist())),
        "ci_hi": dict(zip(names, (beta + crit * se).tolist())),
        "p": dict(zip(names, pval.tolist())),
        "tau2_resid": t2, "tau2_null": tau2_null, "R2": R2, "k": k, "df": df,
    }
    return out


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

def forest_plot(labels, y, lo, hi, weights, pooled: MAResult, path, xlabel,
                title=None, group_labels=None, ref_line=None, figsize=None,
                right_text=None, xlim=None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    k = len(y)
    h = figsize or (8.5, max(3.5, 0.28 * k + 2.2))
    fig, ax = plt.subplots(figsize=h)
    ypos = np.arange(k, 0, -1)
    wn = np.asarray(weights) / np.max(weights)
    for i in range(k):
        ax.plot([lo[i], hi[i]], [ypos[i], ypos[i]], color="#333333", lw=1)
        ax.scatter([y[i]], [ypos[i]], s=20 + 80 * wn[i], marker="s", color="#2b5d8a", zorder=3)
    # pooled diamond
    yd = 0
    d = pooled
    ax.fill([d.ci[0], d.mu, d.ci[1], d.mu], [yd, yd + 0.35, yd, yd - 0.35], color="#b03a2e", zorder=3)
    if not math.isnan(d.pi[0]):
        ax.plot([d.pi[0], d.pi[1]], [yd - 0.6, yd - 0.6], color="#b03a2e", lw=2, alpha=0.6)
    ax.axvline(d.mu, color="#b03a2e", lw=0.8, ls=":")
    if ref_line is not None:
        ax.axvline(ref_line, color="grey", lw=0.8, ls="--")
    ax.set_yticks(list(ypos) + [yd])
    ax.set_yticklabels(list(labels) + [f"Random effects (k={d.k})"], fontsize=8)
    ax.set_xlabel(xlabel)
    if xlim:
        ax.set_xlim(*xlim)
    if right_text is not None:
        trans = ax.get_yaxis_transform()
        for i in range(k):
            ax.text(1.01, ypos[i], right_text[i], transform=trans, fontsize=7, va="center")
        ax.text(1.01, yd, f"{d.mu:.2f} [{d.ci[0]:.2f}, {d.ci[1]:.2f}]", transform=trans,
                fontsize=7, va="center", fontweight="bold")
    txt = (f"I² = {100*d.I2:.0f}%, τ = {d.tau:.2f}; "
           f"95% PI {d.pi[0]:.2f} to {d.pi[1]:.2f}")
    ax.text(0.0, -0.11, txt, transform=ax.transAxes, fontsize=8)
    if title:
        ax.set_title(title, fontsize=10)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_ylim(-1.2, k + 0.8)
    fig.tight_layout()
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def funnel_plot(y, v, mu, path, xlabel):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    se = np.sqrt(np.asarray(v))
    fig, ax = plt.subplots(figsize=(5, 4.5))
    ax.scatter(y, se, color="#2b5d8a", s=18)
    smax = se.max() * 1.1
    ss = np.linspace(0, smax, 50)
    ax.plot(mu - 1.96 * ss, ss, color="grey", ls="--", lw=0.8)
    ax.plot(mu + 1.96 * ss, ss, color="grey", ls="--", lw=0.8)
    ax.axvline(mu, color="#b03a2e", lw=0.8)
    ax.invert_yaxis()
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Standard error")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=300)
    plt.close(fig)
