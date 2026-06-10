from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------------
# Data: benchmark overlap
# -----------------------------
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

# Errors breakdown
ERROR_TYPES = ["Objective", "Constraint", "Syntax", "Format"]
BASELINE_ERRORS = np.array([11, 24, 15, 7])
EMERGE_ERRORS = np.array([1, 7, 14, 2])
N_PER_CATEGORY = 25

# Task order for display
task_order = [
    "ST_SR_IA", "ST_SR_TA", "ST_MR_IA", "ST_MR_TA",
    "MT_SR_IA", "MT_SR_TA", "MT_MR_IA", "MT_MR_TA"
]

# -----------------------------
# Build dataframe
# -----------------------------
rows = []
for task in task_order:
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

df = pd.DataFrame(rows)

# Aggregate totals
agg = df[["Both solved", "EMERGE only", "Baseline only", "Unsolved by both"]].sum()
emerge_total = int(df["EMERGE only"].sum() + df["Both solved"].sum())
baseline_total = int(df["Baseline only"].sum() + df["Both solved"].sum())
net_gain = emerge_total - baseline_total

baseline_error_total = int(BASELINE_ERRORS.sum())
emerge_error_total = int(EMERGE_ERRORS.sum())
error_reduction = baseline_error_total - emerge_error_total
rel_error_reduction = error_reduction / baseline_error_total * 100

# -----------------------------
# Style
# -----------------------------
BLUE = "#4C78A8"
TEAL = "#72B7B2"
ORANGE = "#F58518"
GRAY = "#D9D9D9"
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

# -----------------------------
# Output paths
# -----------------------------
out_dir = Path(__file__).resolve().parent
out_dir.mkdir(parents=True, exist_ok=True)

pdf_path = out_dir / "figure1_final_polished.pdf"

# -----------------------------
# Figure: final polished version
# -----------------------------
fig = plt.figure(figsize=(7.5, 4.2), dpi=300)
gs = fig.add_gridspec(
    2, 3,
    width_ratios=[2.5, 1.0, 1.5],
    height_ratios=[1.0, 0.65],
    wspace=0.36,
    hspace=0.42
)

# (a) Main overlap
ax1 = fig.add_subplot(gs[:, 0])
x = np.arange(len(df))
bottom = np.zeros(len(df))
stack_order = ["Both solved", "EMERGE only", "Baseline only", "Unsolved by both"]

for seg in stack_order:
    vals = df[seg].to_numpy()
    bars = ax1.bar(
        x,
        vals,
        bottom=bottom,
        width=0.72,
        label=seg,
        color={"Both solved": TEAL, "EMERGE only": BLUE, "Baseline only": ORANGE, "Unsolved by both": GRAY}[seg],
        edgecolor="white",
        linewidth=0.6,
    )
    for i, (bar, v) in enumerate(zip(bars, vals)):
        if v >= 2:
            ax1.text(
                bar.get_x() + bar.get_width() / 2,
                bottom[i] + v / 2,
                str(int(v)),
                ha="center",
                va="center",
                fontsize=7.4,
            )
        elif v == 1:
            ax1.text(
                bar.get_x() + bar.get_width() / 2,
                bottom[i] + v / 2,
                "1",
                ha="center",
                va="center",
                fontsize=6.8,
            )
    bottom += vals

# net gain
for i, g in enumerate(df["Net gain"]):
    ax1.text(
        i, N_PER_CATEGORY + 0.75, f"{int(g):+d}",
        ha="center", va="bottom", fontsize=8, fontweight="bold"
    )

ax1.text(len(df) - 0.05, N_PER_CATEGORY + 1.85, "Net gain",
         ha="right", va="bottom", fontsize=7.5)

ax1.set_xticks(x)
ax1.set_xticklabels(df["Task"], rotation=30, ha="right")
ax1.set_ylim(0, N_PER_CATEGORY + 3.0)
ax1.set_ylabel("Number of instances")
ax1.set_xlabel("Task category")
ax1.set_title("(a) Solved-instance overlap across benchmark categories", pad=26)
ax1.grid(axis="y", linestyle=":", linewidth=0.5, alpha=0.6)
ax1.spines["top"].set_visible(False)
ax1.spines["right"].set_visible(False)
ax1.legend(loc="upper center", bbox_to_anchor=(0.5, 1.18),
           ncol=4, frameon=False, columnspacing=1.2, handlelength=1.4)

# (b) Aggregate cards
ax2 = fig.add_subplot(gs[0, 1:])
ax2.axis("off")
cards = [
    ("Solved instances", f"{emerge_total}", f"Baseline {baseline_total}", BLUE),
    ("Net solved gain", f"+{net_gain}", "", TEAL),
    ("Total errors", f"{emerge_error_total}", f"Baseline {baseline_error_total}", ORANGE),
    ("Error reduction", f"{rel_error_reduction:.1f}%", f"{error_reduction} fewer", TEAL),
]
for i, (title, main, sub, color) in enumerate(cards):
    x0 = 0.02 + i*0.235
    width = 0.225
    rect = plt.Rectangle((x0, 0.18), width, 0.62, transform=ax2.transAxes,
                         facecolor="#F7F7F7", edgecolor=LIGHT_BORDER, linewidth=0.8)
    ax2.add_patch(rect)
    ax2.text(x0 + width/2, 0.68, title, transform=ax2.transAxes, ha="center", va="center", fontsize=7.3, color=DARK)
    ax2.text(x0 + width/2, 0.46, main, transform=ax2.transAxes, ha="center", va="center", fontsize=14, fontweight="bold", color=color)
    ax2.text(x0 + width/2, 0.28, sub, transform=ax2.transAxes, ha="center", va="center", fontsize=7.0, color=DARK)

# (c) Error-type dumbbell
ax3 = fig.add_subplot(gs[1, 1:])
y = np.arange(len(ERROR_TYPES))
for i, (b, e) in enumerate(zip(BASELINE_ERRORS, EMERGE_ERRORS)):
    ax3.plot([e, b], [i, i], color="#B0B0B0", linewidth=2.0, zorder=1)
    ax3.scatter(b, i, s=42, color=ORANGE, label="Baseline" if i==0 else "", zorder=2)
    ax3.scatter(e, i, s=42, color=BLUE, label="EMERGE" if i==0 else "", zorder=3)
    ax3.text(b + 0.8, i, str(b), va="center", ha="left", fontsize=7.5, color=ORANGE)
    ax3.text(e - 0.8, i, str(e), va="center", ha="right", fontsize=7.5, color=BLUE)
    ax3.text((b+e)/2, i+0.23, f"-{b-e}", va="center", ha="center", fontsize=7.2, color=DARK)

ax3.set_yticks(y)
ax3.set_yticklabels(ERROR_TYPES)
ax3.invert_yaxis()
ax3.set_xlim(0, max(BASELINE_ERRORS)+4)
ax3.set_xlabel("Number of errors")
ax3.set_title("(c) Error-type reduction over 200 instances", loc="left", pad=5)
ax3.grid(axis="x", linestyle=":", linewidth=0.45, alpha=0.55)
ax3.spines["top"].set_visible(False)
ax3.spines["right"].set_visible(False)
ax3.legend(frameon=False, loc="lower right", ncol=2, handletextpad=0.3)

# Super title and footnote
fig.suptitle("Benchmark-level solved-instance overlap and error diagnosis", fontsize=10.7, fontweight="bold", y=1.02)
fig.text(0.5, -0.015,
         "Panel (a) shows solved-instance overlap per task. Panel (c) categorizes failed cases by error type.",
         ha="center", fontsize=7.2)

# -----------------------------
# Save
# -----------------------------
fig.tight_layout()
fig.savefig(pdf_path, bbox_inches="tight")

print(f"Saved PDF: {pdf_path}")
print(df.to_string(index=False))
