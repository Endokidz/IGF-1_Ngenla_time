"""Minimal PRISMA 2020 flow diagram (database-only template) in matplotlib."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


def prisma(path, identified_lines, removed_lines, screened, excluded_screen, sought, not_retrieved,
           assessed, excluded_full_lines, included_lines):
    fig, ax = plt.subplots(figsize=(8.2, 8.6))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    def box(x, y, w, h, text, bold=False, fc="#ffffff"):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.2",
                                    ec="#52514e", fc=fc, lw=0.9))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=8.2,
                fontweight="bold" if bold else "normal", wrap=True)

    def arrow(x1, y1, x2, y2):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="-|>", color="#52514e", lw=0.9))

    # stage labels
    for y, lab in [(86, "Identification"), (56, "Screening"), (12, "Included")]:
        ax.text(1.5, y, lab, rotation=90, fontsize=9, fontweight="bold", color="#2a78d6", va="center")
    L, R, W = 8, 60, 44
    box(L, 79, W, 15, "\n".join(identified_lines))
    box(R, 79, 38, 15, "\n".join(removed_lines))
    arrow(L + W, 86.5, R, 86.5)
    box(L, 64, W, 9, f"Records screened\n(n = {screened})")
    box(R, 64, 38, 9, f"Records excluded\n(n = {excluded_screen})")
    arrow(L + W / 2, 79, L + W / 2, 73)
    arrow(L + W, 68.5, R, 68.5)
    box(L, 49, W, 9, f"Reports sought for retrieval\n(n = {sought})")
    box(R, 49, 38, 9, f"Reports not retrieved\n(n = {not_retrieved})")
    arrow(L + W / 2, 64, L + W / 2, 58)
    arrow(L + W, 53.5, R, 53.5)
    box(L, 30, W, 11, f"Reports assessed for eligibility\n(n = {assessed})")
    box(R, 25, 38, 20, "\n".join(excluded_full_lines))
    arrow(L + W / 2, 49, L + W / 2, 41)
    arrow(L + W, 35.5, R, 35.5)
    box(L, 3, W, 18, "\n".join(included_lines), bold=True, fc="#eef4fc")
    arrow(L + W / 2, 30, L + W / 2, 21)
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
