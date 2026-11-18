"""Figures for P4 (static, journal-ready PNG at 300 dpi)."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "..", "data")
F = os.path.join(HERE, "..", "figures")
SER = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]
MK = ["o", "s", "^", "D", "v"]
LS = ["-", "--", "-.", ":", (0, (5, 1))]
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": "#e6e6e3", "grid.linewidth": 0.6,
                     "axes.edgecolor": "#52514e", "axes.labelcolor": "#0b0b0b"})

g = pd.read_csv(os.path.join(D, "analytic_grid_s1.csv"))
sim = pd.read_csv(os.path.join(D, "simulation_results.csv"))

# ---- Figure 1: inflation & PPV vs lambda, by technique bias (analytic) ----
fig, axes = plt.subplots(1, 3, figsize=(11, 3.6))
deltas = [0.0, -0.25, -0.5, -1.0]
for i, dlt in enumerate(deltas):
    s = g[g.delta == dlt]
    lab = "no bias" if dlt == 0 else f"bias {dlt:+.2f} SD"
    axes[0].plot(s.lam, s.inflation, color=SER[i], ls=LS[i], lw=2, label=lab)
    axes[1].plot(s.lam, 100 * s.ppv, color=SER[i], ls=LS[i], lw=2, label=lab)
    axes[2].plot(s.lam, 100 * s.sens, color=SER[i], ls=LS[i], lw=2, label=lab)
    # overlay Monte Carlo points
    m = sim[(sim.experiment == "A_error_x_bias") & (sim.strategy == "S1_single") & (sim.delta == dlt)]
    axes[0].scatter(m.lam, m.inflation, color=SER[i], marker=MK[i], s=22, zorder=3, edgecolor="white", linewidth=0.6)
    axes[1].scatter(m.lam, 100 * m.ppv, color=SER[i], marker=MK[i], s=22, zorder=3, edgecolor="white", linewidth=0.6)
    axes[2].scatter(m.lam, 100 * m.sens, color=SER[i], marker=MK[i], s=22, zorder=3, edgecolor="white", linewidth=0.6)
axes[0].set_yscale("log")
axes[0].set_yticks([1, 2, 5, 10, 20])
axes[0].set_yticklabels(["1×", "2×", "5×", "10×", "20×"])
axes[0].set_ylabel("Apparent ÷ true prevalence")
axes[1].set_ylabel("Positive predictive value (%)")
axes[2].set_ylabel("Sensitivity (%)")
for ax, t in zip(axes, ["A  Over-diagnosis", "B  PPV of a 'micropenis' label", "C  Sensitivity"]):
    ax.set_xlabel("Measurement error λ (error SD ÷ population SD)")
    ax.set_title(t, loc="left", fontsize=10, fontweight="bold")
axes[1].set_ylim(0, 102)
axes[2].set_ylim(40, 102)
axes[1].legend(frameon=False, fontsize=8, loc="upper right")
fig.tight_layout()
fig.savefig(os.path.join(F, "Fig1_error_bias_accuracy.png"), dpi=300)
plt.close(fig)

# ---- Figure 2: strategies, PPV & false positives per 10k ----------------
strat = ["S1_single", "S2_mean2_same_observer", "S3_mean2_two_observers", "S4_two_stage_mean", "S5_two_stage_both"]
slab = ["Single measurement", "Mean of 2, same observer", "Mean of 2, two observers",
        "Two-stage, confirm by mean", "Two-stage, both positive"]
fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), sharex=True)
for j, dlt in enumerate([0.0, -0.5]):
    ax = axes[j]
    for i, s in enumerate(strat):
        m = sim[(sim.experiment == "A_error_x_bias") & (sim.strategy == s) & (sim.delta == dlt)].sort_values("lam")
        ax.plot(m.lam, 100 * m.ppv, color=SER[i], ls=LS[i], marker=MK[i], ms=4, lw=1.8, label=slab[i])
    ax.set_ylim(0, 102)
    ax.set_xlabel("Measurement error λ")
    ax.set_ylabel("Positive predictive value (%)")
    ax.set_title(("A  Correct technique (no systematic bias)" if dlt == 0 else
                  "B  Fat pad not depressed (bias −0.5 SD)"), loc="left", fontsize=10, fontweight="bold")
axes[0].legend(frameon=False, fontsize=7.5, loc="upper right")
fig.tight_layout()
fig.savefig(os.path.join(F, "Fig2_mitigation_strategies.png"), dpi=300)
plt.close(fig)

# ---- Figure 3: reference mismatch heat-table ------------------------------
d = sim[(sim.experiment == "D_reference_mismatch") & (sim.strategy == "S1_single")]
piv = d.pivot(index="scale_ref", columns="shift_ref", values="inflation").sort_index(ascending=False)
ppv = d.pivot(index="scale_ref", columns="shift_ref", values="ppv").sort_index(ascending=False)
fig, ax = plt.subplots(figsize=(6.4, 3.0))
# diverging encoding of log2(inflation): blue = under-diagnosis, orange = over-diagnosis, grey = neutral
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
cmap = LinearSegmentedColormap.from_list("div", ["#1c5cab", "#86b6ef", "#e9e8e4", "#f2a27f", "#b8461b"])
val = np.log2(piv.values.clip(1e-3))
im = ax.imshow(val, cmap=cmap, norm=TwoSlopeNorm(vcenter=0, vmin=-6, vmax=6), aspect="auto")
for (r, c), v in np.ndenumerate(piv.values):
    p = ppv.values[r, c]
    ax.text(c, r, f"{v:.2g}×\nPPV {100*p:.0f}%", ha="center", va="center", fontsize=7.5, color="#0b0b0b")
ax.set_xticks(range(piv.shape[1]))
ax.set_xticklabels([f"{x:+.1f}" for x in piv.columns])
ax.set_yticks(range(piv.shape[0]))
ax.set_yticklabels([f"{x:.2f}" for x in piv.index])
ax.set_xlabel("Reference mean − true population mean (true-population SD units)")
ax.set_ylabel("Reference SD ÷ true SD")
ax.grid(False)
cb = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02)
cb.set_label("log₂(apparent ÷ true prevalence)", fontsize=8)
fig.tight_layout()
fig.savefig(os.path.join(F, "Fig3_reference_mismatch.png"), dpi=300)
plt.close(fig)
print("figures written")
