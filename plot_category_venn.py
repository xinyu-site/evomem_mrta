from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle


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


OURS_COLOR = "#4C78A8"
BASELINE_COLOR = "#F58518"


def draw_venn(ax, category, counts):
    only_ours = counts["only_ours"]
    both = counts["both"]
    only_baseline = counts["only_baseline"]
    ours_total = only_ours + both
    baseline_total = only_baseline + both

    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(-1.55, 1.55)
    ax.set_ylim(-1.15, 1.25)

    left = Circle(
        (-0.45, 0),
        0.82,
        facecolor=OURS_COLOR,
        edgecolor=OURS_COLOR,
        alpha=0.42,
        linewidth=1.6,
    )
    right = Circle(
        (0.45, 0),
        0.82,
        facecolor=BASELINE_COLOR,
        edgecolor=BASELINE_COLOR,
        alpha=0.42,
        linewidth=1.6,
    )
    ax.add_patch(left)
    ax.add_patch(right)

    ax.text(-0.9, 0.02, str(only_ours), ha="center", va="center", fontsize=18, fontweight="bold")
    ax.text(0.0, 0.02, str(both), ha="center", va="center", fontsize=18, fontweight="bold")
    ax.text(0.9, 0.02, str(only_baseline), ha="center", va="center", fontsize=18, fontweight="bold")

    ax.text(-0.72, 0.88, "Ours", ha="center", va="center", fontsize=10.5, color=OURS_COLOR, fontweight="bold")
    ax.text(0.72, 0.88, "Baseline", ha="center", va="center", fontsize=10.5, color=BASELINE_COLOR, fontweight="bold")

    ax.text(
        -0.72,
        -0.95,
        f"Ours={ours_total}",
        ha="center",
        va="center",
        fontsize=9.5,
        color="#333333",
    )
    ax.text(
        0.72,
        -0.95,
        f"Baseline={baseline_total}",
        ha="center",
        va="center",
        fontsize=9.5,
        color="#333333",
    )

    ax.set_title(category, fontsize=12, fontweight="bold", pad=7)


def save_single_venn(category, counts, out_dir):
    fig, ax = plt.subplots(figsize=(3.2, 2.7), dpi=300)
    draw_venn(ax, category, counts)
    fig.tight_layout(pad=0.25)
    fig.savefig(out_dir / f"venn_{category}.png", dpi=300, bbox_inches="tight")
    fig.savefig(out_dir / f"venn_{category}.pdf", bbox_inches="tight")
    plt.close(fig)


def save_grid_venn(data, out_dir):
    fig, axes = plt.subplots(2, 4, figsize=(12, 5.8), dpi=300)
    for ax, (category, counts) in zip(axes.flat, data.items()):
        draw_venn(ax, category, counts)

    fig.suptitle("Correctness Overlap by MRTA Category", fontsize=15, fontweight="bold", y=0.98)
    fig.tight_layout(rect=(0, 0, 1, 0.95), pad=0.4)
    fig.savefig(out_dir / "venn_all_categories.png", dpi=300, bbox_inches="tight")
    fig.savefig(out_dir / "venn_all_categories.pdf", bbox_inches="tight")
    plt.close(fig)


def main():
    out_dir = Path("figures") / "venn"
    out_dir.mkdir(parents=True, exist_ok=True)

    for category, counts in DATA.items():
        save_single_venn(category, counts, out_dir)

    save_grid_venn(DATA, out_dir)
    print(f"Saved Venn figures to: {out_dir.resolve()}")


if __name__ == "__main__":
    main()
