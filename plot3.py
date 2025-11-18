import os
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd

# Set font to Times New Roman (use serif family with Times New Roman as first choice)
mpl.rcParams["font.family"] = "serif"
mpl.rcParams["font.serif"] = ["Times New Roman", "Times", "DejaVu Serif", "Liberation Serif"]


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
        'BAE-UQ-IDS': '#2980B9'  # Dark Blue
    }
    
    # Filter Mean metrics (exclude Max metrics)
    mean_metrics = df[df['Metric'].str.contains('Mean', na=False) | df['Metric'].str.contains('Duration', na=False)]
    metrics = mean_metrics['Metric'].values
    x = list(range(len(metrics)))
    bar_width = 0.25
    
    # Plot bars for each method (Mean values)
    methods = ['Snort', 'Snort_Proposed', 'BAE-UQ-IDS']
    positions = [
        [i - bar_width for i in x],  # Snort (left)
        x,  # Snort_Proposed (center)
        [i + bar_width for i in x]   # BAE-UQ-IDS (right)
    ]
    
    # Method display names
    method_display_names = {
        'Snort': 'Snort',
        'Snort_Proposed': 'Snort + FlowSign',
        'BAE-UQ-IDS': 'BAE-UQ-IDS'
    }
    
    # Plot Mean values as bars
    for i, method in enumerate(methods):
        ax.bar(
            positions[i],
            mean_metrics[method].values,
            width=bar_width,
            label=method_display_names.get(method, method.replace('_', ' ')),
            color=colors[method]
        )
    
    # Plot Max values as red lines/markers
    max_metrics = df[df['Metric'].str.contains('Max', na=False)]
    if len(max_metrics) > 0:
        # For each method, plot Max values at corresponding Mean positions
        for method_idx, method in enumerate(methods):
            max_x_vals = []
            max_y_vals = []
            
            for max_metric in max_metrics['Metric'].values:
                # Find corresponding Mean metric position
                if 'CPU_Max' in max_metric:
                    # Find CPU_Mean position
                    for idx, metric in enumerate(mean_metrics['Metric'].values):
                        if 'CPU_Mean' in metric:
                            max_x_vals.append(idx)
                            max_val = df[df['Metric'] == max_metric][method].values[0]
                            max_y_vals.append(max_val)
                            break
                
                elif 'Memory_Max' in max_metric:
                    # Find Memory_Mean position
                    for idx, metric in enumerate(mean_metrics['Metric'].values):
                        if 'Memory_Mean' in metric:
                            max_x_vals.append(idx)
                            max_val = df[df['Metric'] == max_metric][method].values[0]
                            max_y_vals.append(max_val)
                            break
            
            # Plot Max values as red line with markers
            if len(max_x_vals) > 0:
                # Adjust x positions to match method's bar position
                adjusted_x_vals = [positions[method_idx][x] for x in max_x_vals]
                ax.plot(adjusted_x_vals, max_y_vals, 'r-', linewidth=2, marker='o', markersize=8, 
                       label='Max' if method_idx == 0 else '', zorder=10)
    
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

