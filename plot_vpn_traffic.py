import os
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd


def main():
    # CSV file path (relative to this script: ../Results/VPN_traffic.csv)
    base_dir = Path(__file__).resolve().parent
    csv_path = base_dir.parent / "Results" / "VPN_traffic.csv"

    # Avoid issues with minus sign rendering
    mpl.rcParams["axes.unicode_minus"] = False

    # Load data
    df = pd.read_csv(csv_path)

    datasets = df["Dataset"]

    # Bar positions
    x = range(len(datasets))
    bar_width = 0.35

    # A4 half-width size (considering up to 4 datasets)
    fig, axes = plt.subplots(1, 2, figsize=(8, 4))
    fig.patch.set_facecolor('white')

    # ----- F1 Score subplot -----
    ax_f1 = axes[0]
    ax_f1.set_facecolor('white')
    ax_f1.bar(
        [i - bar_width / 2 for i in x],
        df["F1_snort"],
        width=bar_width,
        label="Snort",
        color="#E74C3C",  # Red color for Snort
    )
    ax_f1.bar(
        [i + bar_width / 2 for i in x],
        df["F1_snort_FlowSign"],
        width=bar_width,
        label="Snort + FlowSign",
        color="#27AE60",  # Green color for Snort + FlowSign
    )
    ax_f1.set_title("F1 Score")
    ax_f1.set_xticks(list(x))
    ax_f1.set_xticklabels(datasets)
    ax_f1.set_ylabel("F1 Score (%)")
    ax_f1.grid(True, alpha=0.3, linestyle='--')

    # ----- Accuracy subplot -----
    ax_acc = axes[1]
    ax_acc.set_facecolor('white')
    ax_acc.bar(
        [i - bar_width / 2 for i in x],
        df["Accuracy_snort"],
        width=bar_width,
        label="Snort",
        color="#E74C3C",  # Red color for Snort
    )
    ax_acc.bar(
        [i + bar_width / 2 for i in x],
        df["Accuracy_snort_FlowSign"],
        width=bar_width,
        label="Snort + FlowSign",
        color="#27AE60",  # Green color for Snort + FlowSign
    )
    ax_acc.set_title("Accuracy")
    ax_acc.set_xticks(list(x))
    ax_acc.set_xticklabels(datasets)
    ax_acc.set_ylabel("Accuracy (%)")
    ax_acc.grid(True, alpha=0.3, linestyle='--')

    # Add a single legend at the top center of the figure
    # Get handles and labels from one of the subplots
    handles, labels = ax_f1.get_legend_handles_labels()
    fig.legend(handles, labels, 
               loc='upper center', 
               ncol=2, 
               frameon=True,
               bbox_to_anchor=(0.5, 0.98))

    fig.suptitle("Snort vs Snort + FlowSign Performance Comparison", fontsize=14, fontweight="bold")
    fig.tight_layout(rect=[0, 0.03, 1, 0.92])

    # Output folder: ../Graph
    graph_dir = base_dir.parent / "Graph"
    os.makedirs(graph_dir, exist_ok=True)

    # Save image (e.g., ../Graph/vpn_traffic_performance.png)
    output_path = graph_dir / "vpn_traffic_performance.png"
    plt.savefig(output_path, dpi=300)

    # 화면에 표시
    plt.show()


if __name__ == "__main__":
    main()



