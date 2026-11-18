"""Figure 1 for the SPL-REF protocol: study schema."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures", "Fig1_study_schema.png")
fig, ax = plt.subplots(figsize=(10, 6.2))
ax.set_xlim(0, 100)
ax.set_ylim(0, 64)
ax.axis("off")
C = {"A": "#2a78d6", "B": "#1baf7a", "C": "#eb6834", "ink": "#0b0b0b", "mute": "#52514e"}


def box(x, y, w, h, title, body, col):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3,rounding_size=1.2", ec=col, fc="white", lw=1.6))
    ax.add_patch(FancyBboxPatch((x, y + h - 5.2), w, 5.2, boxstyle="round,pad=0.3,rounding_size=1.2", ec=col, fc=col, lw=1.6))
    ax.text(x + 1.2, y + h - 2.6, title, color="white", fontsize=9.5, fontweight="bold", va="center")
    ax.text(x + 1.2, y + h - 7.0, body, color=C["ink"], fontsize=7.4, va="top", linespacing=1.45)


def arrow(x1, y1, x2, y2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="-|>", color=C["mute"], lw=1))


ax.text(50, 62.5, "SPL-REF: three linked components, one standardised technique", ha="center", fontsize=11, fontweight="bold")
box(1, 25, 31, 34, "A  Cross-sectional reference, 0–18 y",
    "Enrol ≈4,500 → analysable 4,000–4,279\n"
    "Age composition uniform on age^0.75\n"
    "+25% over-sampling at 9–15 y\n\n"
    "Duplicate SPL (fat pad depressed)\n"
    "Duplicate SPL, fat pad NOT depressed (≥2 y)\n"
    "Height, weight, waist, Tanner, testis vol.\n\n"
    "Target: SE ≤0.10 z at −2.5 SD centile", C["A"])
box(34.5, 25, 31, 34, "B  Neonatal cohort + minipuberty",
    "1,000 term newborns at 24–72 h\n"
    "Duplicate SPL; GA, birth-weight SDS,\n"
    "maternal & perinatal covariates\n\n"
    "Nested longitudinal sub-cohort (n = 155)\n"
    "SPL at birth, 4, 8, 12 wk, 6 mo\n"
    "Blood at 6–10 wk: testosterone (LC-MS/MS),\n"
    "LH, FSH, SHBG, AMH, INSL3", C["B"])
box(68, 25, 31, 34, "C  Reliability & technique",
    "240 boys (4 age strata × 60)\n"
    "3 certified examiners per child\n"
    "With vs without fat-pad depression\n\n"
    "ICC(2,1), TEM, Bland–Altman\n"
    "Variance components: child /\n"
    "examiner / residual by age\n"
    "λ = σ_error / σ_SPL", C["C"])
# outputs
outs = [(1, "GAMLSS centiles 0–18 y\n(observed-scale & error-corrected)"),
        (25.7, "Neonatal reference by GA;\nminipuberty growth–testosterone"),
        (50.4, "Fat-pad correction by\nBMI-SDS; Tanner-conditional refs"),
        (75.1, "Measurement-error model;\nfree online SDS calculator")]
for x, t in outs:
    ax.add_patch(FancyBboxPatch((x, 3), 23.9, 11, boxstyle="round,pad=0.3,rounding_size=1.2", ec=C["mute"], fc="#f3f2ef", lw=0.9))
    ax.text(x + 11.95, 8.5, t, ha="center", va="center", fontsize=8)
ax.text(50, 18.2, "Outputs", ha="center", fontsize=9.5, fontweight="bold", color=C["mute"])
for x in (16.5, 50, 83.5):
    arrow(x, 25, x, 19.6)
ax.text(50, 0.4, "Common to all components: certified examiners (TEM ≤ 2 mm vs lead), rigid acrylic ruler, "
        "no photography, chaperone ≥7 y, REDCap data capture", ha="center", fontsize=7.5, color=C["mute"])
fig.savefig(OUT, dpi=300, bbox_inches="tight")
print("ok")
