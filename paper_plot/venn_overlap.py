from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


DATA = {
    "MT_MR_IA": {"only_ours": 6, "both": 19, "only_baseline": 0},
    "MT_MR_TA": {"only_ours": 14, "both": 2, "only_baseline": 0},
    "MT_SR_IA": {"only_ours": 0, "both": 22, "only_baseline": 2},
    "MT_SR_TA": {"only_ours": 17, "both": 1, "only_baseline": 2},
    "ST_MR_IA": {"only_ours": 1, "both": 24, "only_baseline": 0},
    "ST_MR_TA": {"only_ours": 5, "both": 17, "only_baseline": 1},
    "ST_SR_IA": {"only_ours": 4, "both": 21, "only_baseline": 0},
    "ST_SR_TA": {"only_ours": 7, "both": 15, "only_baseline": 0},
}

N_PER_CATEGORY = 25
TASK_ORDER = [
    "ST_SR_IA", "ST_SR_TA", "ST_MR_IA", "ST_MR_TA",
    "MT_SR_IA", "MT_SR_TA", "MT_MR_IA", "MT_MR_TA"
]

BLUE = "#4C78A8"
TEAL = "#72B7B2"
ORANGE = "#F58518"
GRAY = "#D9D9D9"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9,
    "axes.titlesize": 10,
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})


rows = []
for task in TASK_ORDER:
    c = DATA[task]
    union = c["only_ours"] + c["both"] + c["only_baseline"]
    neither = N_PER_CATEGORY - union
    rows.append({
        "Task": task,
        "Both solved": c["both"],
        "EMERGE only": c["only_ours"],
        "CLGA only": c["only_baseline"],
        "Unsolved by both": neither,
        "Net gain": c["only_ours"] - c["only_baseline"],
    })

fig, ax = plt.subplots(figsize=(5.2, 3.6), dpi=300)
x = np.arange(len(rows))
bottom = np.zeros(len(rows))
stack_order = ["Both solved", "EMERGE only", "CLGA only", "Unsolved by both"]
colors = {
    "Both solved": TEAL,
    "EMERGE only": BLUE,
    "CLGA only": ORANGE,
    "Unsolved by both": GRAY,
}

for seg in stack_order:
    vals = np.array([row[seg] for row in rows])
    bars = ax.bar(
        x,
        vals,
        bottom=bottom,
        width=0.72,
        label=seg,
        color=colors[seg],
        edgecolor="white",
        linewidth=0.6,
    )
    for i, (bar, v) in enumerate(zip(bars, vals)):
        if v >= 2:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bottom[i] + v / 2,
                str(int(v)),
                ha="center",
                va="center",
                fontsize=7.4,
            )
        elif v == 1:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bottom[i] + v / 2,
                "1",
                ha="center",
                va="center",
                fontsize=6.8,
            )
    bottom += vals

for i, row in enumerate(rows):
    ax.text(
        i,
        N_PER_CATEGORY + 0.75,
        f"{int(row['Net gain']):+d}",
        ha="center",
        va="bottom",
        fontsize=8,
        fontweight="bold",
    )

ax.set_xticks(x)
ax.set_xticklabels([row["Task"] for row in rows], rotation=30, ha="right")
ax.set_ylim(0, N_PER_CATEGORY + 3.0)
ax.set_ylabel("Number of instances")
ax.set_xlabel("Task category")
ax.grid(axis="y", linestyle=":", linewidth=0.5, alpha=0.6)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.14),
          ncol=4, frameon=False, columnspacing=1.2, handlelength=1.4)

fig.tight_layout()
pdf_path = Path(__file__).resolve().parent / "venn_overlap.pdf"
fig.savefig(pdf_path, bbox_inches="tight")

print(f"Saved PDF: {pdf_path}")
for row in rows:
    print(row)
