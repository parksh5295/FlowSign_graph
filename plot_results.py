import os
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd


def main():
    # Base directory
    base_dir = Path(__file__).resolve().parent
    results_dir = base_dir.parent / "Results"
    
    # Avoid issues with minus sign rendering
    mpl.rcParams["axes.unicode_minus"] = False
    
    # Load data from three CSV files
    df2 = pd.read_csv(results_dir / "result2.csv")
    df3 = pd.read_csv(results_dir / "result3.csv")
    df4 = pd.read_csv(results_dir / "result4.csv")
    
    # Prepare data for plotting
    datasets = [
        ("Performance Metrics", df2),
        ("Resource Metrics", df3),
        ("Processing Metrics", df4)
    ]
    
    # A4 half-width size (A4 width = 8.27 inches, half = ~4 inches)
    # 3 subplots, so slightly wider but still within A4 half-width
    fig, axes = plt.subplots(1, 3, figsize=(4.5, 3.5))
    fig.patch.set_facecolor('white')
    
    # Color scheme
    colors = {
        'Snort': '#E74C3C',  # Red
        'Snort_Proposed': '#27AE60',  # Green
        'SoTA_ML': '#3498DB'  # Blue
    }
    
    for idx, (title, df) in enumerate(datasets):
        ax = axes[idx]
        ax.set_facecolor('white')
        
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
        
        ax.set_title(title, fontsize=10)
        ax.set_xticks(x)
        ax.set_xticklabels(metrics, fontsize=8)
        ax.set_ylabel("Value", fontsize=9)
        ax.tick_params(axis='y', labelsize=8)
        ax.grid(True, alpha=0.3, linestyle='--')
    
    # Add a single legend at the top center, above the graph area
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels,
               loc='upper center',
               ncol=3,
               frameon=True,
               fontsize=9,
               bbox_to_anchor=(0.5, 1.0),
               bbox_transform=fig.transFigure)
    
    fig.tight_layout(rect=[0, 0.08, 1, 0.90])
    
    # Output folder: ../Graph
    graph_dir = base_dir.parent / "Graph"
    os.makedirs(graph_dir, exist_ok=True)
    
    # Save image
    output_path = graph_dir / "results_comparison.png"
    plt.savefig(output_path, dpi=300)
    
    # Display
    plt.show()


if __name__ == "__main__":
    main()

