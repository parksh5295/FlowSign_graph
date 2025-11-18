import os
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd

# Set font to Times New Roman (use serif family with Times New Roman as first choice)
mpl.rcParams["font.family"] = "serif"
mpl.rcParams["font.serif"] = ["Times New Roman", "Times", "DejaVu Serif", "Liberation Serif"]


def plot_metric_subplot(ax, df, metric_mean_name, metric_max_name, methods, method_columns, 
                        color_map, default_color, method_display_names, bar_width, title):
    """Plot a single metric subplot with Mean bars and Max horizontal lines."""
    # Get Mean values
    mean_row = df[df['Metric'] == metric_mean_name]
    if len(mean_row) == 0:
        return
    
    # Position for grouped bars (single group of bars)
    x_center = 0.5
    num_methods = len(methods)
    positions = []
    for i in range(num_methods):
        offset = (i - (num_methods - 1) / 2) * bar_width
        positions.append(x_center + offset)
    
    # Plot Mean values as bars
    for i, method in enumerate(methods):
        method_col = method_columns[i]
        mean_val = mean_row[method_col].values[0]
        display_name = method_display_names.get(method, method.replace('_', ' ').replace('-', ' '))
        color = color_map.get(method, default_color)
        
        ax.bar(
            positions[i],
            mean_val,
            width=bar_width,
            label=display_name if metric_mean_name == 'Duration(s)' else '',  # Only label in first subplot
            color=color
        )
    
    # Plot Max values as horizontal red lines (if Max metric exists)
    if metric_max_name:
        max_row = df[df['Metric'] == metric_max_name]
        if len(max_row) > 0:
            for i, method in enumerate(methods):
                method_col = method_columns[i]
                max_val = max_row[method_col].values[0]
                # Draw horizontal line at max value, spanning the bar width
                x_start = positions[i] - bar_width / 2
                x_end = positions[i] + bar_width / 2
                ax.plot([x_start, x_end], [max_val, max_val], 'r-', linewidth=2, 
                       label='Max' if i == 0 and metric_mean_name == 'CPU_Mean(%)' else '', zorder=10)
    
    # Set title and formatting
    ax.set_title(title, fontsize=78)
    ax.set_xticks([])  # No x-axis labels for individual subplots
    ax.tick_params(axis='y', labelsize=72)
    # Remove decimal points from y-axis
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x)}'))
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xlim(-0.2, 1.2)


def main():
    # Base directory
    base_dir = Path(__file__).resolve().parent
    results_dir = base_dir.parent / "Results"
    
    # Avoid issues with minus sign rendering
    mpl.rcParams["axes.unicode_minus"] = False
    
    # Load result3.csv
    df = pd.read_csv(results_dir / "result3.csv")
    
    # Get actual column names (handle any potential column name issues)
    actual_columns = df.columns.tolist()
    # Remove 'Metric' column to get method names
    method_columns = [col for col in actual_columns if col != 'Metric']
    
    # Match plot4.py's figure size and layout
    fig_width = 36  # Same as plot4.py
    fig, axes = plt.subplots(1, 3, figsize=(fig_width, 18))  # 3 subplots horizontally
    fig.patch.set_facecolor('white')
    
    # Color scheme - unified dark colors
    color_map = {
        'Snort': '#C0392B',  # Dark Red
        'Snort_Proposed': '#229954',  # Dark Green
    }
    # Default color for other methods
    default_color = '#2980B9'  # Dark Blue
    
    # Method display names
    method_display_names = {
        'Snort': 'Snort',
        'Snort_Proposed': 'Snort + FlowSign',
    }
    
    # Map method_columns to method names (for display)
    methods = []
    for col in method_columns:
        if col == 'Snort':
            methods.append('Snort')
        elif col == 'Snort_Proposed':
            methods.append('Snort_Proposed')
        else:
            methods.append(col)  # Use column name as-is for others
    
    bar_width = 0.4  # Wider bars to fill the graph area
    
    # Metric names and titles
    metrics_info = [
        ('Duration(s)', None, 'Duration (s)', 0),  # No Max for Duration
        ('CPU_Mean(%)', 'CPU_Max(%)', 'CPU (%)', 1),
        ('Memory_Mean(MB)', 'Memory_Max(MB)', 'Memory (MB)', 2)
    ]
    
    for metric_mean_name, metric_max_name, title, idx in metrics_info:
        ax = axes[idx]
        ax.set_facecolor('white')
        
        plot_metric_subplot(ax, df, metric_mean_name, metric_max_name, methods, method_columns,
                           color_map, default_color, method_display_names, bar_width, title)
    
    # Add a single legend at the top center, above all subplots
    # Collect handles and labels from all axes to ensure all methods are included
    all_handles = []
    all_labels = []
    seen_labels = set()
    
    # First, collect all handles and labels from all axes
    for ax in axes:
        handles, labels = ax.get_legend_handles_labels()
        for handle, label in zip(handles, labels):
            if label and label not in seen_labels:
                all_handles.append(handle)
                all_labels.append(label)
                seen_labels.add(label)
    
    # If some methods are missing, add them manually
    for method in methods:
        display_name = method_display_names.get(method, method.replace('_', ' ').replace('-', ' '))
        if display_name not in seen_labels:
            from matplotlib.patches import Rectangle
            method_col = method_columns[methods.index(method)]
            color = color_map.get(method, default_color)
            dummy_handle = Rectangle((0, 0), 1, 1, facecolor=color, edgecolor='black')
            all_handles.append(dummy_handle)
            all_labels.append(display_name)
            seen_labels.add(display_name)
    
    # Add Max to legend if not already present
    if 'Max' not in seen_labels:
        from matplotlib.lines import Line2D
        max_handle = Line2D([0], [0], color='red', linewidth=2)
        all_handles.append(max_handle)
        all_labels.append('Max')
    
    fig.legend(all_handles, all_labels,
               loc='upper center',
               ncol=4,
               frameon=True,
               fontsize=76,  # Match plot4.py
               bbox_to_anchor=(0.5, 1.03),
               bbox_transform=fig.transFigure)
    
    fig.tight_layout(rect=[0.02, 0.01, 1, 0.90])  # Match plot4.py
    
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
