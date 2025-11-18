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
    # Adjust bar width based on number of datasets
    bar_width = 0.3 if len(datasets) > 2 else 0.35

    # A4 half-width size (A4 width = 8.27 inches, half = ~4 inches)
    # Increase figure size to accommodate larger text (similar to paper body text)
    fig_width = 36 if len(datasets) > 2 else 33  # Wider for larger text
    fig, axes = plt.subplots(1, 2, figsize=(fig_width, 18))  # Reduced height
    fig.patch.set_facecolor('white')

    # ----- F1 Score subplot -----
    ax_f1 = axes[0]
    ax_f1.set_facecolor('white')
    ax_f1.bar(
        [i - bar_width / 2 for i in x],
        df["F1_snort"],
        width=bar_width,
        label="Snort",
        color="#C0392B",  # Dark Red for Snort
    )
    ax_f1.bar(
        [i + bar_width / 2 for i in x],
        df["F1_snort_FlowSign"],
        width=bar_width,
        label="Snort + FlowSign",
        color="#229954",  # Dark Green for Snort + FlowSign
    )
    ax_f1.set_title("F1 Score", fontsize=84)
    ax_f1.set_xticks(list(x))
    ax_f1.set_xticklabels(datasets, fontsize=80, rotation=90, ha='center')
    ax_f1.set_ylabel("F1 Score (%)", fontsize=82)
    ax_f1.set_ylim(0, 100)
    ax_f1.tick_params(axis='y', labelsize=78)
    ax_f1.grid(True, alpha=0.3, linestyle='--')

    # ----- Accuracy subplot -----
    ax_acc = axes[1]
    ax_acc.set_facecolor('white')
    ax_acc.bar(
        [i - bar_width / 2 for i in x],
        df["Accuracy_snort"],
        width=bar_width,
        label="Snort",
        color="#C0392B",  # Dark Red for Snort
    )
    ax_acc.bar(
        [i + bar_width / 2 for i in x],
        df["Accuracy_snort_FlowSign"],
        width=bar_width,
        label="Snort + FlowSign",
        color="#229954",  # Dark Green for Snort + FlowSign
    )
    ax_acc.set_title("Accuracy", fontsize=84)
    ax_acc.set_xticks(list(x))
    ax_acc.set_xticklabels(datasets, fontsize=80, rotation=90, ha='center')
    ax_acc.set_ylabel("Accuracy (%)", fontsize=82)
    ax_acc.set_ylim(0, 100)
    ax_acc.tick_params(axis='y', labelsize=78)
    ax_acc.grid(True, alpha=0.3, linestyle='--')

    # Add a single legend at the top center, above the graph area
    # Get handles and labels from one of the subplots
    handles, labels = ax_f1.get_legend_handles_labels()
    fig.legend(handles, labels, 
               loc='upper center', 
               ncol=2, 
               frameon=True,
               fontsize=82,
               bbox_to_anchor=(0.5, 1.03),
               bbox_transform=fig.transFigure)
    
    fig.tight_layout(rect=[0, 0.01, 1, 0.90])

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



