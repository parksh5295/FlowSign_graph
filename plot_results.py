import os
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd


def plot_single_result(df, title, output_path):
    """Plot a single result CSV file as a separate graph."""
    # A4 half-width size (A4 width = 8.27 inches, half = ~4 inches)
    fig, ax = plt.subplots(1, 1, figsize=(8, 3.5))  # 2x width, original height
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    
    # Color scheme
    colors = {
        'Snort': '#E74C3C',  # Red
        'Snort_Proposed': '#27AE60',  # Green
        'SoTA_ML': '#3498DB'  # Blue
    }
    
    metrics = df['Metric'].values
    x = list(range(len(metrics)))
    bar_width = 0.25
    
    # Plot bars for each method
    methods = ['Snort', 'Snort_Proposed', 'SoTA_ML']
    positions = [
        [i - bar_width for i in x],  # Snort (left)
        x,  # Snort_Proposed (center)
        [i + bar_width for i in x]   # SoTA_ML (right)
    ]
    
    for i, method in enumerate(methods):
        ax.bar(
            positions[i],
            df[method],
            width=bar_width,
            label=method.replace('_', ' '),
            color=colors[method]
        )
    
    ax.set_title(title, fontsize=30)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, fontsize=24)
    ax.set_ylabel("Value", fontsize=27)
    ax.tick_params(axis='y', labelsize=24)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Add legend at the top center, above the graph area
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels,
               loc='upper center',
               ncol=3,
               frameon=True,
               fontsize=27,
               bbox_to_anchor=(0.5, 1.0),
               bbox_transform=fig.transFigure)
    
    fig.tight_layout(rect=[0, 0.02, 1, 0.95])
    
    # Save image
    plt.savefig(output_path, dpi=300)
    plt.close()


def main():
    # Base directory
    base_dir = Path(__file__).resolve().parent
    results_dir = base_dir.parent / "Results"
    
    # Avoid issues with minus sign rendering
    mpl.rcParams["axes.unicode_minus"] = False
    
    # Output folder: ../Graph
    graph_dir = base_dir.parent / "Graph"
    os.makedirs(graph_dir, exist_ok=True)
    
    # Load and plot each CSV file separately
    datasets = [
        ("result2.csv", "Performance Metrics", "result2_performance.png"),
        ("result3.csv", "Resource Metrics", "result3_resource.png"),
        ("result4.csv", "Processing Metrics", "result4_processing.png")
    ]
    
    for csv_file, title, output_file in datasets:
        df = pd.read_csv(results_dir / csv_file)
        output_path = graph_dir / output_file
        plot_single_result(df, title, output_path)
        print(f"Saved: {output_path}")
    
    print("All graphs generated successfully!")


if __name__ == "__main__":
    main()

