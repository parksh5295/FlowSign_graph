import os
from pathlib import Path
import numpy as np

import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd


def add_break_symbol(ax, y_break_pos, x_center=0.5, width=1.5):
    """Add a double wavy break symbol (~~~~) with white fill inside to indicate axis break."""
    from matplotlib.patches import Polygon
    from matplotlib.path import Path
    
    # Create two wavy lines (double line, parallel)
    x_data = np.linspace(x_center - width/2, x_center + width/2, 200)
    y_range = ax.get_ylim()[1] - ax.get_ylim()[0]
    
    # Common wave pattern (same amplitude for parallel lines)
    wave_pattern = 0.01 * y_range * np.sin(15 * np.pi * (x_data - (x_center - width/2)) / width)
    
    # First wavy line (outer, upper) - parallel to second line
    # Create clear gap between two lines
    y_data1 = y_break_pos + 0.015 * y_range + wave_pattern
    
    # Second wavy line (inner, lower) - parallel to first line
    y_data2 = y_break_pos + 0.005 * y_range + wave_pattern
    
    # Create polygon path for white fill between the two wavy lines
    # Combine outer line (forward) and inner line (backward) to form closed path
    polygon_points = np.vstack([
        np.column_stack([x_data, y_data1]),  # Outer line forward
        np.column_stack([x_data[::-1], y_data2[::-1]])  # Inner line backward
    ])
    
    # Fill the area between the two wavy lines with white
    poly = Polygon(polygon_points, facecolor='white', edgecolor='none', zorder=13, transform=ax.transData)
    ax.add_patch(poly)
    
    # Draw the two wavy lines
    ax.plot(x_data, y_data1, 'k-', linewidth=3, clip_on=False, zorder=15)
    ax.plot(x_data, y_data2, 'k-', linewidth=3, clip_on=False, zorder=15)
    
    # Add small vertical lines at ends
    ax.plot([x_center - width/2, x_center - width/2], 
            [y_break_pos - 0.008 * y_range, 
             y_break_pos + 0.008 * y_range], 
            'k-', linewidth=3, clip_on=False, zorder=15)
    ax.plot([x_center + width/2, x_center + width/2], 
            [y_break_pos - 0.008 * y_range, 
             y_break_pos + 0.008 * y_range], 
            'k-', linewidth=3, clip_on=False, zorder=15)
    
    # Draw white rectangle to cover top spine in the break area
    from matplotlib.patches import Rectangle
    rect = Rectangle((x_center - width/2, y_break_pos - 0.01 * y_range), 
                     width, 0.025 * y_range,
                     facecolor='white', edgecolor='none', zorder=12, transform=ax.transData)
    ax.add_patch(rect)


def plot_metric(ax, df, metric_name, methods, colors, bar_width):
    """Plot bars for a metric, with broken axis if values differ significantly."""
    values = [df[df['Metric'] == metric_name][method].values[0] for method in methods]
    max_val = max(values)
    min_val = min(values)
    
    # Position for grouped bars (single group of 3 bars)
    x_center = 0.5
    
    # Check if we need broken axis (only for Throughput, and if max is more than 3x min and both > 0)
    needs_break = (metric_name == 'Throughput' and 
                   max_val > 0 and min_val > 0 and max_val / min_val > 3)
    
    if needs_break:
        # For Throughput: show 0-15 range, then break, then 370-400 range
        low_max = 15  # Upper limit of lower range
        high_min = 360  # Lower limit of upper range
        high_max = max_val * 1.1  # Upper limit of upper range
        
        # Plot bars (grouped)
        positions = [x_center - bar_width, x_center, x_center + bar_width]
        
        # Separate low and high values
        low_values = []
        high_values = []
        low_positions = []
        high_positions = []
        low_methods = []
        high_methods = []
        
        for i, method in enumerate(methods):
            val = df[df['Metric'] == metric_name][method].values[0]
            if val <= low_max:
                low_values.append(val)
                low_positions.append(positions[i])
                low_methods.append((method, i))
            else:
                high_values.append(val)
                high_positions.append(positions[i])
                high_methods.append((method, i))
        
        # Plot low values in lower range
        for (method, orig_i), pos, val in zip(low_methods, low_positions, low_values):
            ax.bar(
                pos,
                val,
                width=bar_width,
                label=method.replace('_', ' ') if metric_name == 'Avg_Processing_Time' else '',
                color=colors[method]
            )
        
        # Set y-axis to show lower range (0-20)
        ax.set_ylim(0, 20)
        
        # Add break symbol at top of lower range (slightly lower position)
        # x-axis range is -0.2 to 1.2, so keep width within this range
        add_break_symbol(ax, 16, x_center=0.5, width=1.0)
        
        # Keep top spine visible but it will be covered by the break symbol
        ax.spines['top'].set_visible(True)
        
        # Set y-axis ticks for lower range
        ax.set_yticks([0, 5, 10, 15])
        
        # Create second y-axis range for high values (using twinx approach)
        # Instead, we'll plot high values scaled to upper range
        # But first, let's use a different approach: plot high values in a transformed coordinate
        
        # Plot high values scaled to fit in upper part of visible area
        for (method, orig_i), pos, val in zip(high_methods, high_positions, high_values):
            # Scale high value to fit in upper range (17-20)
            # Map from [high_min, high_max] to [17, 20]
            scaled_val = 17 + (val - high_min) / (high_max - high_min) * 3
            ax.bar(
                pos,
                scaled_val,
                width=bar_width,
                color=colors[method],
                alpha=0.7
            )
            # Add text annotation with actual value (lower position to avoid boundary)
            ax.text(pos, 18.5, f'{val:.1f}',
                   ha='center', va='bottom', fontsize=21, color=colors[method], weight='bold')
        
        # Add custom y-axis label for upper range
        # Create a second set of ticks for upper range
        upper_ticks = np.linspace(high_min, int(high_max), 5)
        upper_tick_positions = 17 + (upper_ticks - high_min) / (high_max - high_min) * 3
        # Add secondary y-axis labels on the right
        ax2 = ax.twinx()
        ax2.set_ylim(ax.get_ylim())
        ax2.set_yticks(upper_tick_positions)
        ax2.set_yticklabels([f'{int(t)}' for t in upper_ticks], fontsize=20)
        ax2.spines['right'].set_visible(True)
        ax2.spines['top'].set_visible(False)
        ax2.spines['left'].set_visible(False)
        ax2.spines['bottom'].set_visible(False)
    else:
        # Plot normally
        positions = [x_center - bar_width, x_center, x_center + bar_width]
        for i, method in enumerate(methods):
            val = df[df['Metric'] == metric_name][method].values[0]
            ax.bar(
                positions[i],
                val,
                width=bar_width,
                label=method.replace('_', ' ') if metric_name == 'Avg_Processing_Time' else '',
                color=colors[method]
            )
        ax.set_ylim(0, max_val * 1.2 if max_val > 0 else 1)
    
    ax.set_xlim(-0.2, 1.2)
    ax.set_xticks([])


def main():
    # Base directory
    base_dir = Path(__file__).resolve().parent
    results_dir = base_dir.parent / "Results"
    
    # Avoid issues with minus sign rendering
    mpl.rcParams["axes.unicode_minus"] = False
    
    # Load result4.csv
    df = pd.read_csv(results_dir / "result4.csv")
    
    # A4 half-width size, 3 subplots horizontally
    # Increase figure size to accommodate 3x larger text
    fig, axes = plt.subplots(1, 3, figsize=(36, 10.5))  # 3 subplots horizontally, 3x text
    fig.patch.set_facecolor('white')
    
    # Color scheme
    colors = {
        'Snort': '#E74C3C',  # Red
        'Snort_Proposed': '#27AE60',  # Green
        'SoTA_ML': '#3498DB'  # Blue
    }
    
    methods = ['Snort', 'Snort_Proposed', 'SoTA_ML']
    bar_width = 0.25
    
    # Metric names and y-axis labels (horizontal layout)
    metrics_info = [
        ('Avg_Processing_Time', 'Avg Processing Time (ms)', 0),
        ('p95_Latency', 'p95 Latency (ms)', 1),
        ('Throughput', 'Throughput (ops/s)', 2)
    ]
    
    for metric_name, ylabel, idx in metrics_info:
        ax = axes[idx]
        ax.set_facecolor('white')
        
        # Plot metric with potential broken axis
        plot_metric(ax, df, metric_name, methods, colors, bar_width)
        
        ax.set_title(metric_name.replace('_', ' '), fontsize=30)
        ax.set_ylabel(ylabel, fontsize=27)
        ax.tick_params(axis='y', labelsize=24)
        ax.grid(True, alpha=0.3, linestyle='--')
    
    # Add a single legend at the top center, above all subplots
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels,
               loc='upper center',
               ncol=3,
               frameon=True,
               fontsize=27,
               bbox_to_anchor=(0.5, 1.02),
               bbox_transform=fig.transFigure)
    
    fig.tight_layout(rect=[0, 0.02, 1, 0.92])
    
    # Output folder: ../Graph
    graph_dir = base_dir.parent / "Graph"
    os.makedirs(graph_dir, exist_ok=True)
    
    # Save image
    output_path = graph_dir / "result4_processing.png"
    plt.savefig(output_path, dpi=300)
    plt.close()
    
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()

