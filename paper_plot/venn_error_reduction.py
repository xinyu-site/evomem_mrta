from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


# -----------------------------
# Data
# -----------------------------
ERROR_TYPES = [
    "Optimization\nobjective",
    "Constraint\ncondition",
    "Syntax",
    "Output\nformat",
]

BASELINE_ERRORS = np.array([11, 24, 15, 7])
EMERGE_ERRORS = np.array([1, 7, 14, 2])

baseline_total = int(BASELINE_ERRORS.sum())
emerge_total = int(EMERGE_ERRORS.sum())
total_cases = 200

# -----------------------------
# Style
# -----------------------------
BASELINE_COLOR = "#F58518"
EMERGE_COLOR = "#4C78A8"
DARK = "#222222"
GRID_COLOR = "#C9C9C9"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9.2,
    "axes.titlesize": 10.2,
    "axes.labelsize": 9,
    "xtick.labelsize": 8.4,
    "ytick.labelsize": 8.4,
    "legend.fontsize": 8.2,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

# -----------------------------
# Plot
# -----------------------------
fig, ax = plt.subplots(figsize=(4.15, 2.65), dpi=300)

x = np.arange(len(ERROR_TYPES))
width = 0.34

baseline_bars = ax.bar(
    x - width / 2,
    BASELINE_ERRORS,
    width,
    label=f"CLGA ({baseline_total}/{total_cases})",
    color=BASELINE_COLOR,
    edgecolor="white",
    linewidth=0.7,
)

emerge_bars = ax.bar(
    x + width / 2,
    EMERGE_ERRORS,
    width,
    label=f"EMERGE ({emerge_total}/{total_cases})",
    color=EMERGE_COLOR,
    edgecolor="white",
    linewidth=0.7,
)

# Value labels
for bars in [baseline_bars, emerge_bars]:
    for bar in bars:
        value = int(bar.get_height())
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + 0.55,
            str(value),
            ha="center",
            va="bottom",
            fontsize=8.0,
            color=DARK,
        )

# Axes
ax.set_ylabel("Number of errors")
ax.set_xticks(x)
ax.set_xticklabels(ERROR_TYPES)
ax.set_ylim(0, 28)
ax.set_axisbelow(True)

# Title
# Put legend inside the axes to avoid outside margins
ax.legend(
    frameon=False,
    loc="upper right",
    handlelength=1.3,
    borderaxespad=0.3,
)

# Grid and spines
ax.grid(axis="y", linestyle=":", linewidth=0.55, color=GRID_COLOR, alpha=0.75)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_color("#9A9A9A")
ax.spines["bottom"].set_color("#9A9A9A")

# Slightly reduce side margins
ax.margins(x=0.06)

fig.tight_layout(pad=0.45)

# -----------------------------
# Save
# -----------------------------
try:
    out_dir = Path(__file__).resolve().parent
except NameError:
    out_dir = Path.cwd()

png_path = out_dir / "error_type_distribution.png"
pdf_path = out_dir / "error_type_distribution.pdf"

fig.savefig(png_path, dpi=300, bbox_inches="tight")
fig.savefig(pdf_path, bbox_inches="tight")

print(f"Saved PNG: {png_path}")
print(f"Saved PDF: {pdf_path}")

plt.show()
