"""
Scatter-plot and centile-curve digitiser for published figures.

Workflow (semi-automatic, auditable):
  1. detect_axes(img)            -> pixel rows/cols of the x- and y-axis lines
  2. detect_ticks(img, axes)     -> pixel positions of tick marks on each axis
  3. The analyst reads the tick LABELS from the image and supplies the mapping
     {pixel: value} for >= 2 ticks per axis (calibrate()). Linear or log axes.
  4. detect_markers(img, ...)    -> marker centroids (pixels); overlapping
     clusters are split by area relative to the modal single-marker area
  5. trace_curve(img, color)     -> y(x) for a coloured/line-style centile curve
  6. to_data()                   -> pixel -> data coordinates
Every run writes a JSON audit record (calibration, thresholds, counts) and an
overlay PNG so a human can verify each detected point against the original.

Dependencies: numpy, scipy, Pillow, matplotlib (overlay only).
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass, asdict, field
from typing import Optional

import numpy as np
from PIL import Image
from scipy import ndimage


def load(path):
    im = Image.open(path).convert("RGB")
    return np.asarray(im).astype(np.int16)


def darkness(img):
    return 255 - img.mean(axis=2)


# ---------------------------------------------------------------------------
# Axes and ticks
# ---------------------------------------------------------------------------

def detect_axes(img, dark_thr=110, min_frac=0.45):
    """Find the x-axis (long dark horizontal line, lowest such line) and the
    y-axis (long dark vertical line, leftmost such line)."""
    d = darkness(img) > dark_thr
    H, W = d.shape
    row_runs = np.array([_longest_run(d[r, :]) for r in range(H)])
    col_runs = np.array([_longest_run(d[:, c]) for c in range(W)])
    rows = np.where(row_runs >= min_frac * W)[0]
    cols = np.where(col_runs >= min_frac * H)[0]
    if len(rows) == 0 or len(cols) == 0:
        raise ValueError("axes not found; lower min_frac or dark_thr")
    x_axis_row = int(_cluster_last(rows))
    y_axis_col = int(_cluster_first(cols))
    # plot extent along each axis
    xr = d[x_axis_row, :]
    yc = d[:, y_axis_col]
    x_span = _run_bounds(xr, y_axis_col)
    y_span = _run_bounds(yc, x_axis_row)
    return dict(x_axis_row=x_axis_row, y_axis_col=y_axis_col, x_span=x_span, y_span=y_span)


def detect_ticks(img, axes, dark_thr=110, tick_len=(3, 25), inside=False, regular=True):
    """Ticks = short dark perpendicular segments touching the axis.
    By default only OUTSIDE ticks are used (inside ticks are confusable with data
    points touching the axis); set inside=True for figures with inward ticks.
    regular=True keeps only ticks consistent with the modal tick spacing."""
    d = darkness(img) > dark_thr
    r0, c0 = axes["x_axis_row"], axes["y_axis_col"]
    xt, yt = [], []
    lo, hi = tick_len
    x0, x1 = axes["x_span"]
    for c in range(x0, x1 + 1):
        below = _run_from(d[r0 + 2:, c])
        above = _run_from(d[:r0 - 1, c][::-1]) if inside else 0
        if lo <= below <= hi or lo <= above <= hi:
            xt.append(c)
    y0, y1 = axes["y_span"]
    for r in range(y0, y1 + 1):
        left = _run_from(d[r, :c0 - 1][::-1])
        right = _run_from(d[r, c0 + 2:]) if inside else 0
        if lo <= left <= hi or lo <= right <= hi:
            yt.append(r)
    xt, yt = _merge_adjacent(xt), _merge_adjacent(yt)
    if regular:
        xt, yt = _regularise(xt), _regularise(yt)
    return dict(x_ticks=xt, y_ticks=yt)


def _regularise(t, tol=0.12):
    """Keep the longest chain of ticks whose spacing matches the modal spacing."""
    if len(t) < 3:
        return t
    t = sorted(t)
    diffs = np.diff(t)
    step = float(np.median(diffs))
    best = []
    for i in range(len(t)):
        chain = [t[i]]
        for x in t[i + 1:]:
            k = round((x - chain[-1]) / step)
            if k >= 1 and abs((x - chain[-1]) - k * step) <= tol * step and k == 1:
                chain.append(x)
        if len(chain) > len(best):
            best = chain
    return best


# ---------------------------------------------------------------------------
# Calibration
# ---------------------------------------------------------------------------

@dataclass
class Axis:
    pix: list
    val: list
    log: bool = False

    def fit(self):
        p = np.asarray(self.pix, float)
        v = np.asarray(self.val, float)
        v = np.log10(v) if self.log else v
        A = np.column_stack([p, np.ones_like(p)])
        (a, b), res, *_ = np.linalg.lstsq(A, v, rcond=None)
        self.a, self.b = float(a), float(b)
        pred = a * p + b
        self.max_resid = float(np.max(np.abs(pred - v))) if len(p) > 2 else 0.0
        return self

    def __call__(self, px):
        v = self.a * np.asarray(px, float) + self.b
        return 10 ** v if self.log else v


def calibrate(x_ticks_pix, x_vals, y_ticks_pix, y_vals, xlog=False, ylog=False):
    ax = Axis(list(x_ticks_pix), list(x_vals), xlog).fit()
    ay = Axis(list(y_ticks_pix), list(y_vals), ylog).fit()
    return ax, ay


# ---------------------------------------------------------------------------
# Markers
# ---------------------------------------------------------------------------

def marker_mask(img, axes, color=None, tol=60, dark_thr=110, pad=3, remove_lines=True, fill=True):
    """Boolean mask of candidate marker pixels inside the plot area.
    color: RGB tuple for coloured markers; None = any dark pixel."""
    H, W, _ = img.shape
    if color is None:
        m = darkness(img) > dark_thr
    else:
        dist = np.sqrt(((img - np.array(color)) ** 2).sum(axis=2))
        m = dist < tol
    r0, c0 = axes["x_axis_row"], axes["y_axis_col"]
    y0, _ = axes["y_span"]
    _, x1 = axes["x_span"]
    box = np.zeros_like(m)
    box[y0:r0 - pad, c0 + pad:x1 + 1] = True
    m &= box
    if remove_lines:
        # remove straight runs spanning >= half the plot (gridlines, reference
        # lines); shorter runs are kept because chains of overlapping markers
        # can be long but never span the plot
        Lx = int(0.5 * (x1 - c0))
        Ly = int(0.5 * (r0 - y0))
        for r in range(H):
            _zero_long_runs(m[r, :], Lx)
        for c in range(W):
            _zero_long_runs(m[:, c], Ly)
    if fill:
        m = ndimage.binary_fill_holes(m)
    return m


def detect_markers(mask, min_area=4, single_area=None, split_at=1.35):
    """Connected components -> centroids; split clusters by area/single_area."""
    lab, n = ndimage.label(mask)
    if n == 0:
        return np.empty((0, 2)), dict(n_components=0)
    idx = np.arange(1, n + 1)
    areas = ndimage.sum(mask, lab, idx)
    keep = areas >= min_area
    idx, areas = idx[keep], areas[keep]
    if single_area is None:
        # modal single-marker area = median of the lower half of component areas
        single_area = float(np.median(areas[areas <= np.median(areas) * 1.3]))
    pts = []
    mult = []
    for i, a in zip(idx, areas):
        # overlap shrinks the union area, so a cluster of k markers has area
        # < k * single; split from split_at x single (validated: see validate.py)
        r = a / single_area
        k = 1 if r < split_at else int(np.floor(r - split_at + 1.0)) + 1
        ys, xs = np.where(lab == i)
        if k == 1:
            pts.append((xs.mean(), ys.mean()))
        else:
            # k-means split of the cluster pixels into k centroids
            P = np.column_stack([xs, ys]).astype(float)
            C = _kmeans(P, k)
            pts.extend([tuple(c) for c in C])
        mult.append(k)
    info = dict(n_components=int(len(idx)), single_area=single_area, n_points=int(len(pts)),
                n_split_clusters=int(sum(1 for m in mult if m > 1)))
    return np.array(pts), info


def trace_curve(img, axes, color, tol=50, pad=3):
    """For a coloured curve: per pixel column, the median row of matching pixels."""
    dist = np.sqrt(((img - np.array(color)) ** 2).sum(axis=2))
    m = dist < tol
    r0, c0 = axes["x_axis_row"], axes["y_axis_col"]
    y0, _ = axes["y_span"]
    _, x1 = axes["x_span"]
    xs, ys = [], []
    for c in range(c0 + pad, x1):
        rows = np.where(m[y0:r0 - pad, c])[0]
        if len(rows):
            xs.append(c)
            ys.append(y0 + float(np.median(rows)))
    return np.array(xs), np.array(ys)


def to_data(pts_pix, ax, ay):
    if len(pts_pix) == 0:
        return np.empty((0, 2))
    return np.column_stack([ax(pts_pix[:, 0]), ay(pts_pix[:, 1])])


def overlay(img, pts_pix, path, axes=None, ticks=None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    H, W, _ = img.shape
    fig, ax = plt.subplots(figsize=(W / 100, H / 100), dpi=100)
    ax.imshow(img.astype(np.uint8))
    if len(pts_pix):
        ax.scatter(pts_pix[:, 0], pts_pix[:, 1], s=14, facecolors="none", edgecolors="#e3008c", linewidths=0.9)
    if axes:
        ax.axhline(axes["x_axis_row"], color="#00a0ff", lw=0.6)
        ax.axvline(axes["y_axis_col"], color="#00a0ff", lw=0.6)
    if ticks:
        for c in ticks["x_ticks"]:
            ax.plot([c, c], [axes["x_axis_row"] + 2, axes["x_axis_row"] + 12], color="#ff8c00", lw=0.8)
        for r in ticks["y_ticks"]:
            ax.plot([axes["y_axis_col"] - 12, axes["y_axis_col"] - 2], [r, r], color="#ff8c00", lw=0.8)
    ax.axis("off")
    fig.subplots_adjust(0, 0, 1, 1)
    fig.savefig(path, dpi=100)
    plt.close(fig)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _longest_run(v):
    best = cur = 0
    for x in v:
        cur = cur + 1 if x else 0
        best = max(best, cur)
    return best


def _run_from(v):
    n = 0
    for x in v:
        if x:
            n += 1
        else:
            break
    return n


def _run_bounds(v, anchor):
    lo = anchor
    while lo > 0 and v[lo - 1]:
        lo -= 1
    hi = anchor
    while hi < len(v) - 1 and v[hi + 1]:
        hi += 1
    return (int(lo), int(hi))


def _cluster_last(idx):
    groups = np.split(idx, np.where(np.diff(idx) > 1)[0] + 1)
    return int(np.mean(groups[-1]))


def _cluster_first(idx):
    groups = np.split(idx, np.where(np.diff(idx) > 1)[0] + 1)
    return int(np.mean(groups[0]))


def _merge_adjacent(v):
    if not v:
        return []
    v = sorted(v)
    groups, cur = [], [v[0]]
    for x in v[1:]:
        if x - cur[-1] <= 1:
            cur.append(x)
        else:
            groups.append(cur)
            cur = [x]
    groups.append(cur)
    return [float(np.mean(g)) for g in groups]


def _zero_long_runs(v, L):
    n = len(v)
    i = 0
    while i < n:
        if v[i]:
            j = i
            while j < n and v[j]:
                j += 1
            if j - i >= L:
                v[i:j] = False
            i = j
        else:
            i += 1


def _kmeans(P, k, iters=50, seed=0):
    rng = np.random.default_rng(seed)
    C = P[rng.choice(len(P), k, replace=False)]
    for _ in range(iters):
        d = ((P[:, None, :] - C[None, :, :]) ** 2).sum(axis=2)
        a = d.argmin(axis=1)
        newC = np.array([P[a == j].mean(axis=0) if np.any(a == j) else C[j] for j in range(k)])
        if np.allclose(newC, C):
            break
        C = newC
    return C
