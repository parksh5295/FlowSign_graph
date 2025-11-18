import os
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd

# Set font to Times New Roman
mpl.rcParams["font.family"] = "Times New Roman"


def main():
    # Base directory
    base_dir = Path(__file__).resolve().parent
    results_dir = base_dir.parent / "Results"
    
    # Avoid issues with minus sign rendering
    mpl.rcParams["axes.unicode_minus"] = False
    
    # Load result3.csv
    df = pd.read_csv(results_dir / "result3.csv")
    
    # Match plot1.py's figure size and font size ratios
    fig_width = 36  # Same as plot1.py
    fig, ax = plt.subplots(1, 1, figsize=(fig_width, 18))  # Reduced height
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    
    # Color scheme - unified dark colors (same as plot1.py and plot4.py)
    colors = {
        'Snort': '#C0392B',  # Dark Red
        'Snort_Proposed': '#229954',  # Dark Green
        'SoTA_ML': '#2980B9'  # Dark Blue
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
    
    # Method display names (match plot1.py and plot4.py)
    method_display_names = {
        'Snort': 'Snort',
        'Snort_Proposed': 'Snort + FlowSign',
        'SoTA_ML': 'SoTA ML'
    }
    
    for i, method in enumerate(methods):
        ax.bar(
            positions[i],
            df[method],
            width=bar_width,
            label=method_display_names.get(method, method.replace('_', ' ')),
            color=colors[method]
        )
    
    # Match plot1.py's font sizes
    ax.set_title("Resource Metrics", fontsize=84)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, fontsize=80)
    ax.set_ylabel("Value", fontsize=82)
    ax.tick_params(axis='y', labelsize=78)
    # Remove decimal points from y-axis
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x)}'))
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Add legend at the top center, above the graph area
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels,
               loc='upper center',
               ncol=3,
               frameon=True,
               fontsize=82,  # Match plot1.py
               bbox_to_anchor=(0.5, 1.03),  # Match plot1.py
               bbox_transform=fig.transFigure)
    
    fig.tight_layout(rect=[0, 0.01, 1, 0.90])  # Match plot1.py
    
    # Output folder: ../Graph
    graph_dir = base_dir.parent / "Graph"
    os.makedirs(graph_dir, exist_ok=True)
    
    # Save image
    output_path = graph_dir / "result3_resource.png"
    plt.savefig(output_path, dpi=300)
    plt.close()
    
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()

