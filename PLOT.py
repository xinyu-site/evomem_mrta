import matplotlib.pyplot as plt

# =========================
# Data
# =========================
robots = {
    "R0": (0.0, 4.0),
    "R1": (1.0, 3.0),
    "R2": (2.0, 0.0),
}

tasks = {
    "T0": (0.0, 3.0),
    "T1": (2.0, 1.0),
    "T2": (2.0, 2.0),
}

# Colors
robot_color = "#1f4ae5"
task_color = "#f57c00"

# =========================
# Figure: smaller version
# =========================
fig, ax = plt.subplots(figsize=(3.6, 3.4), dpi=300)
ax.set_axisbelow(True)

# =========================
# Plot robots
# =========================
for name, (x, y) in robots.items():
    ax.scatter(
        x, y,
        s=85,
        c=robot_color,
        marker="o",
        zorder=5,
        clip_on=False
    )
    ax.text(
        x + 0.07, y + 0.12, name,
        fontsize=9.5,
        color=robot_color,
        fontstyle="italic",
        fontweight="bold",
        zorder=6
    )

# =========================
# Plot tasks
# =========================
for name, (x, y) in tasks.items():
    ax.scatter(
        x, y,
        s=75,
        c=task_color,
        marker="s",
        zorder=5,
        clip_on=False
    )
    ax.text(
        x + 0.07, y + 0.10, name,
        fontsize=9.5,
        color=task_color,
        fontstyle="italic",
        fontweight="bold",
        zorder=6
    )

# =========================
# Task callouts
# =========================
callout_style = dict(
    boxstyle="round,pad=0.25",
    fc="white",
    ec=task_color,
    lw=0.9,
)

arrow_style = dict(
    arrowstyle="-",
    color=task_color,
    lw=0.9,
)

ax.annotate(
    "T0\nneed 2 robots",
    xy=tasks["T0"],
    xytext=(0.58, 2.42),
    fontsize=7.8,
    ha="center",
    va="center",
    bbox=callout_style,
    arrowprops=arrow_style,
    zorder=7
)

ax.annotate(
    "T1\nneed 1 robot",
    xy=tasks["T1"],
    xytext=(2.62, 1.15),
    fontsize=7.8,
    ha="center",
    va="center",
    bbox=callout_style,
    arrowprops=arrow_style,
    zorder=7
)

ax.annotate(
    "T2\nneed 1 robot",
    xy=tasks["T2"],
    xytext=(2.62, 2.15),
    fontsize=7.8,
    ha="center",
    va="center",
    bbox=callout_style,
    arrowprops=arrow_style,
    zorder=7
)

# =========================
# Axes and grid
# =========================
ax.set_xlim(-0.25, 3.15)
ax.set_ylim(-0.25, 5.15)

ax.set_xticks([0, 1, 2, 3])
ax.set_yticks([0, 1, 2, 3, 4, 5])

ax.tick_params(labelsize=8.5)

ax.grid(
    True,
    linestyle="--",
    linewidth=0.6,
    alpha=0.45
)

ax.set_xlabel(r"$x$", fontsize=10.5)
ax.set_ylabel(r"$y$", fontsize=10.5, rotation=0)

ax.yaxis.set_label_coords(-0.08, 1.02)
ax.xaxis.set_label_coords(1.02, -0.05)

# 如果想更省空间，可以注释掉标题
ax.set_title("2D Workspace", fontsize=10.5, fontweight="bold", pad=6)

for spine in ax.spines.values():
    spine.set_linewidth(0.8)

# =========================
# Legend inside axes
# =========================
robot_handle = ax.scatter([], [], s=85, c=robot_color, marker="o", label="Robots")
task_handle = ax.scatter([], [], s=75, c=task_color, marker="s", label="Tasks")

ax.legend(
    handles=[robot_handle, task_handle],
    loc="lower left",
    bbox_to_anchor=(0.03, 0.03),
    ncol=1,
    frameon=True,
    fontsize=7.8,
    borderpad=0.35,
    labelspacing=0.3,
    handletextpad=0.4,
)

# =========================
# Save
# =========================
plt.tight_layout(pad=0.4)

plt.savefig("mrta_workspace_example_small.png", dpi=300, bbox_inches="tight")
plt.savefig("mrta_workspace_example_small.pdf", bbox_inches="tight")

plt.show()