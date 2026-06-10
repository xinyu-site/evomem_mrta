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

BASELINE_ERRORS = np.array([11, 24, 15, 7])
EMERGE_ERRORS = np.array([1, 7, 14, 2])
N_PER_CATEGORY = 25
TASK_ORDER = [
    "ST_SR_IA", "ST_SR_TA", "ST_MR_IA", "ST_MR_TA",
    "MT_SR_IA", "MT_SR_TA", "MT_MR_IA", "MT_MR_TA"
]

BLUE = "#4C78A8"
TEAL = "#72B7B2"
ORANGE = "#F58518"
DARK = "#222222"
LIGHT_BORDER = "#CFCFCF"

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
        "Baseline only": c["only_baseline"],
        "Unsolved by both": neither,
        "Net gain": c["only_ours"] - c["only_baseline"],
    })

emerge_total = int(sum(row["EMERGE only"] + row["Both solved"] for row in rows))
baseline_total = int(sum(row["Baseline only"] + row["Both solved"] for row in rows))
net_gain = emerge_total - baseline_total

baseline_error_total = int(BASELINE_ERRORS.sum())
emerge_error_total = int(EMERGE_ERRORS.sum())
error_reduction = baseline_error_total - emerge_error_total
rel_error_reduction = error_reduction / baseline_error_total * 100

fig, ax = plt.subplots(figsize=(4.8, 1.35), dpi=300)
ax.axis("off")

cards = [
    ("Solved instances", f"{emerge_total}", f"Baseline {baseline_total}", BLUE),
    ("Net solved gain", f"+{net_gain}", "", TEAL),
    ("Total errors", f"{emerge_error_total}", f"Baseline {baseline_error_total}", ORANGE),
    ("Error reduction", f"{rel_error_reduction:.1f}%", f"{error_reduction} fewer", TEAL),
]

for i, (title, main, sub, color) in enumerate(cards):
    x0 = 0.02 + i * 0.235
    width = 0.225
    rect = plt.Rectangle(
        (x0, 0.18),
        width,
        0.62,
        transform=ax.transAxes,
        facecolor="#F7F7F7",
        edgecolor=LIGHT_BORDER,
        linewidth=0.8,
    )
    ax.add_patch(rect)
    ax.text(x0 + width / 2, 0.68, title, transform=ax.transAxes,
            ha="center", va="center", fontsize=7.3, color=DARK)
    ax.text(x0 + width / 2, 0.46, main, transform=ax.transAxes,
            ha="center", va="center", fontsize=14, fontweight="bold", color=color)
    ax.text(x0 + width / 2, 0.28, sub, transform=ax.transAxes,
            ha="center", va="center", fontsize=7.0, color=DARK)

fig.tight_layout()
pdf_path = Path(__file__).resolve().parent / "venn_summary_cards.pdf"
fig.savefig(pdf_path, bbox_inches="tight")

print(f"Saved PDF: {pdf_path}")
