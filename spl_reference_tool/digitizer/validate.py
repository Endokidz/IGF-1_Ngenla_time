"""
Validate the digitiser on synthetic published-style figures with KNOWN data.

For each style we draw a figure from known (age, SPL) points, run the digitiser
using automatic axis/tick detection (tick values supplied exactly as an analyst
would read them off the image), and compare:
  * number of points recovered vs true
  * point-level error (nearest-neighbour, data units)
  * age-bin mean and SD recovered vs true (what the calculator actually uses)
"""
import json
import os
import sys

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import digitize as dz  # noqa: E402

OUT = os.path.join(HERE, "validation")
os.makedirs(OUT, exist_ok=True)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def make_data(n, seed):
    rng = np.random.default_rng(seed)
    age = rng.uniform(0, 18, n)
    # smooth, plausible SPL growth (synthetic; used ONLY for validation)
    mu = 3.4 + 0.9 * np.log1p(age) + 4.5 / (1 + np.exp(-(age - 13.5) / 1.2))
    sd = 0.35 + 0.045 * age
    spl = rng.normal(mu, sd)
    return age, np.clip(spl, 1.0, 17.5)


def draw(age, spl, path, style):
    fig, ax = plt.subplots(figsize=(6.4, 4.4), dpi=150)
    if style == "filled_black":
        ax.scatter(age, spl, s=10, color="black")
    elif style == "hollow_grid":
        ax.grid(True, color="#bbbbbb", lw=0.6)
        ax.scatter(age, spl, s=16, facecolors="none", edgecolors="black", linewidths=0.8)
    elif style == "dense_grey":
        ax.scatter(age, spl, s=7, color="#555555")
    ax.set_xlim(0, 18)
    ax.set_ylim(0, 18)
    ax.set_xticks(range(0, 19, 2))
    ax.set_yticks(range(0, 19, 3))
    ax.tick_params(direction="out", length=5, width=1)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_xlabel("Age (years)")
    ax.set_ylabel("SPL (cm)")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def bins(age, spl):
    edges = [0, 2, 5, 9, 12, 15, 18.01]
    out = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (age >= lo) & (age < hi)
        out.append((lo, hi, int(m.sum()), float(spl[m].mean()), float(spl[m].std(ddof=1))))
    return out


def run_style(style, n, seed, color=None):
    age, spl = make_data(n, seed)
    p = os.path.join(OUT, f"{style}.png")
    draw(age, spl, p, style)
    img = dz.load(p)
    axes = dz.detect_axes(img)
    ticks = dz.detect_ticks(img, axes)
    xt, yt = ticks["x_ticks"], ticks["y_ticks"]
    # Analyst step: map detected ticks to labels read from the image.
    # x ticks are 0,2,...,18 (10 ticks); y ticks are 0,3,...,18 (7 ticks, bottom-up).
    assert len(xt) == 10, f"{style}: x ticks found {len(xt)}"
    assert len(yt) == 7, f"{style}: y ticks found {len(yt)}"
    ax, ay = dz.calibrate(xt, list(range(0, 19, 2)), sorted(yt, reverse=True), list(range(0, 19, 3)))
    mask = dz.marker_mask(img, axes, color=color, remove_lines=True)
    pts_pix, info = dz.detect_markers(mask)
    pts = dz.to_data(pts_pix, ax, ay)
    dz.overlay(img, pts_pix, os.path.join(OUT, f"{style}_overlay.png"), axes, ticks)
    tree = cKDTree(np.column_stack([age, spl]))
    dist, _ = tree.query(pts)
    tb, rb = bins(age, spl), bins(pts[:, 0], pts[:, 1])
    rows = []
    for (lo, hi, n_t, m_t, s_t), (_, _, n_r, m_r, s_r) in zip(tb, rb):
        rows.append(dict(style=style, bin=f"{lo:g}-{hi:g}", n_true=n_t, n_rec=n_r, mean_true=m_t, mean_rec=m_r,
                         mean_err=m_r - m_t, sd_true=s_t, sd_rec=s_r, sd_err=s_r - s_t))
    summ = dict(style=style, n_true=n, n_recovered=int(len(pts)), recovery_pct=100 * len(pts) / n,
                median_point_err=float(np.median(dist)), p95_point_err=float(np.percentile(dist, 95)),
                calib_resid_x=ax.max_resid, calib_resid_y=ay.max_resid, **info)
    return summ, rows


def run_curves():
    """Centile curves (3rd/50th/97th) drawn as coloured lines; trace and compare."""
    a = np.linspace(0, 18, 200)
    mu = 3.4 + 0.9 * np.log1p(a) + 4.5 / (1 + np.exp(-(a - 13.5) / 1.2))
    sd = 0.35 + 0.045 * a
    curves = {"#1f4e9a": mu - 1.881 * sd, "#000000": mu, "#c0392b": mu + 1.881 * sd}
    fig, ax = plt.subplots(figsize=(6.4, 4.4), dpi=150)
    for c, y in curves.items():
        ax.plot(a, y, color=c, lw=1.6)
    ax.set_xlim(0, 18); ax.set_ylim(0, 18)
    ax.set_xticks(range(0, 19, 2)); ax.set_yticks(range(0, 19, 3))
    ax.tick_params(direction="out", length=5, width=1)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    p = os.path.join(OUT, "centile_curves.png")
    fig.savefig(p); plt.close(fig)
    img = dz.load(p)
    axes = dz.detect_axes(img)
    ticks = dz.detect_ticks(img, axes)
    ax_, ay_ = dz.calibrate(ticks["x_ticks"], list(range(0, 19, 2)), sorted(ticks["y_ticks"], reverse=True), list(range(0, 19, 3)))
    errs = {}
    for c, ytrue in curves.items():
        rgb = tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))
        xs, ys = dz.trace_curve(img, axes, rgb, tol=60)
        xd, yd = ax_(xs), ay_(ys)
        yt = np.interp(xd, a, ytrue)
        ok = (xd > 0.3) & (xd < 17.7)
        errs[c] = dict(n_cols=int(ok.sum()), median_abs_err=float(np.median(np.abs(yd[ok] - yt[ok]))),
                       max_abs_err=float(np.max(np.abs(yd[ok] - yt[ok]))))
    return errs


if __name__ == "__main__":
    summaries, allrows = [], []
    for style, n, seed in [("filled_black", 300, 1), ("hollow_grid", 300, 2), ("dense_grey", 800, 3)]:
        s, r = run_style(style, n, seed)
        summaries.append(s)
        allrows += r
    curves = run_curves()
    pd.DataFrame(summaries).to_csv(os.path.join(OUT, "validation_summary.csv"), index=False)
    pd.DataFrame(allrows).to_csv(os.path.join(OUT, "validation_bins.csv"), index=False)
    json.dump(curves, open(os.path.join(OUT, "validation_curves.json"), "w"), indent=2)
    pd.set_option("display.width", 220)
    print(pd.DataFrame(summaries).round(3).to_string(index=False))
    print(pd.DataFrame(allrows).round(3).to_string(index=False))
    print(json.dumps(curves, indent=1))
