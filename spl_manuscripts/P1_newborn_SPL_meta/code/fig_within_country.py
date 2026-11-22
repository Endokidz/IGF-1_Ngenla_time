import os, json
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
D, F = os.path.join(HERE, "..", "data"), os.path.join(HERE, "..", "figures")
u = pd.read_csv(os.path.join(D, "analysis_dataset.csv"))
r = json.load(open(os.path.join(D, "results.json")))
u["country0"] = u["country"].str.split("(").str[0].str.strip()
cnt = u.groupby("country0")["study_id"].nunique()
order = sorted(cnt.index, key=lambda c: (-cnt[c], -u[u.country0 == c]["mean"].mean()))
fig, ax = plt.subplots(figsize=(7.6, 0.42 * len(order) + 1.6))
pm = r["pooled_mean"]
ax.axvspan(pm["pi_lo"], pm["pi_hi"], color="#e9e8e4", zorder=0, label="95% prediction interval, all populations")
ax.axvline(pm["mu"], color="#b03a2e", lw=1, ls=":", zorder=1)
for i, c in enumerate(order):
    y = len(order) - 1 - i
    g = u[u.country0 == c]
    multi = cnt[c] >= 2
    col = "#2a78d6" if multi else "#8a8984"
    if multi:
        ax.plot([g["mean"].min(), g["mean"].max()], [y, y], color=col, lw=1.2, alpha=0.6, zorder=2)
    ax.scatter(g["mean"], [y] * len(g), s=12 + g["n"] / 6, color=col, edgecolor="white", linewidth=0.7, zorder=3)
    ax.text(4.32, y, f"{cnt[c]} stud{'ies' if cnt[c] > 1 else 'y'}", fontsize=7.5, va="center", color="#52514e")
ax.set_yticks(range(len(order)))
ax.set_yticklabels(order[::-1], fontsize=8.5)
ax.set_xlim(2.2, 4.3)
ax.set_xlabel("Study mean stretched penile length, term newborns (cm)")
ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="x", color="#ecebe8", lw=0.6)
w = json.load(open(os.path.join(D, "within_country_results.json")))["multi_country_subset"]
ax.set_title(f"Within-country spread ≈ global spread: {100*w['share_within']:.0f}% of between-study variance lies within countries",
             fontsize=9, loc="left")
ax.legend(frameon=False, fontsize=7.5, loc="lower right")
fig.tight_layout()
fig.savefig(os.path.join(F, "Fig4_within_country.png"), dpi=300)
print("ok")
