# subplot

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
    # Create clear gap between two lines (1.5x wider than before)
    y_data1 = y_break_pos + 0.025 * y_range + wave_pattern
    
    # Second wavy line (inner, lower) - parallel to first line
    y_data2 = y_break_pos + 0.0025 * y_range + wave_pattern
    
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


def plot_metric(ax, df, metric_name, methods, colors, bar_width, method_display_names=None):
    """Plot bars for a metric, with broken axis if values differ significantly."""
    if method_display_names is None:
        method_display_names = {m: m.replace('_', ' ') for m in methods}
    
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
                label=method_display_names.get(method, method.replace('_', ' ')) if metric_name == 'Avg_Processing_Time' else '',
                color=colors[method]
            )
            # Add text annotation for low values too
            ax.text(pos, val + 0.5, f'{val:.1f}',
                   ha='center', va='bottom', fontsize=21, color=colors[method], weight='bold')
        
        # Find the middle point between SoTA ML (low values) and Snort/Snort+FlowSign (high values)
        # SoTA ML max is around 15, high values start at 27, so middle is around 21
        sota_ml_max = max(low_values) if low_values else 15
        high_start = 27  # Where high values start
        break_position = (sota_ml_max + high_start) / 2  # Middle position
        
        # Set y-axis ticks for lower range
        # Add high value ticks above the break (370-400 range) on the left y-axis
        # Lower range ticks: 0, 5, 10, 15 (with gap before break)
        lower_ticks = [0, 5, 10, 15]
        
        # High value ticks: use 5-unit spacing (same as 15-10 spacing)
        # Start from high_min rounded to nearest 5, then add 5, 10, 15, 20
        start_tick = int(np.ceil(high_min / 5) * 5)  # Round up to nearest 5
        high_tick_values = [start_tick + i * 5 for i in range(5) if start_tick + i * 5 <= int(high_max)]
        
        # Map to y-axis positions with SAME VISUAL SPACING as lower ticks
        # Lower ticks: 0, 5, 10, 15 are spaced 5 units apart visually
        # Upper ticks should also be spaced 5 units apart visually (not compressed)
        num_ticks = len(high_tick_values)
        if num_ticks > 1:
            # Use 27 to 27 + (num_ticks-1)*5 to maintain 5-unit visual spacing
            high_tick_positions = [27 + i * 5 for i in range(num_ticks)]
        else:
            high_tick_positions = [27 + (t - high_min) / (high_max - high_min) * 5 for t in high_tick_values]
        
        # Set y-axis range to accommodate upper ticks with 5-unit spacing
        y_max = 27 + (num_ticks - 1) * 5 + 3 if num_ticks > 1 else 35  # Add some padding at top
        ax.set_ylim(0, y_max)
        
        # Add break symbol at middle position between SoTA ML and high values
        # x-axis range is -0.2 to 1.2, so keep width within this range
        add_break_symbol(ax, break_position, x_center=0.5, width=1.0)
        
        # Keep top spine visible but it will be covered by the break symbol
        ax.spines['top'].set_visible(True)
        
        # Combine lower and upper ticks (gap between 15 and 27 shows the break)
        all_ticks = lower_ticks + high_tick_positions
        all_tick_labels = ['0', '5', '10', '15'] + [f'{int(t)}' for t in high_tick_values]
        
        # Set ticks and labels
        ax.set_yticks(all_ticks)
        ax.set_yticklabels(all_tick_labels, fontsize=24)
        
        # Plot high values scaled to fit in upper part of visible area
        # Keep Snort and Snort + FlowSign at higher position to maintain bar length (27-32 range)
        for (method, orig_i), pos, val in zip(high_methods, high_positions, high_values):
            # Scale high value to fit in upper range (27-32) - maintain bar length, slightly higher
            # Map from [high_min, high_max] to [27, 32]
            scaled_val = 27 + (val - high_min) / (high_max - high_min) * 5
            ax.bar(
                pos,
                scaled_val,
                width=bar_width,
                color=colors[method],
                alpha=0.7
            )
            # Add text annotation with actual value (similar spacing to SoTA ML)
            # SoTA ML uses val + 0.5, so use scaled_val + 0.5 for similar spacing
            ax.text(pos, scaled_val + 0.5, f'{val:.1f}',
                   ha='center', va='bottom', fontsize=21, color=colors[method], weight='bold')
    else:
        # Plot normally (for Avg_Processing_Time and p95_Latency)
        # Use similar approach to Throughput: separate low and high values
        positions = [x_center - bar_width, x_center, x_center + bar_width]
        
        # Separate low and high values (similar to Throughput logic)
        # Low values: Snort and Snort+FlowSign (typically small)
        # High values: SoTA ML (typically large)
        low_values = []
        high_values = []
        low_positions = []
        high_positions = []
        low_methods = []
        high_methods = []
        
        # Determine threshold: if max is much larger than min, use broken axis
        sorted_vals = sorted(values)
        if len(sorted_vals) >= 2 and sorted_vals[-1] > sorted_vals[0] * 10:
            # Significant gap exists, use broken axis approach
            # For Avg_Processing_Time and p95_Latency: 
            # Snort and Snort+FlowSign are low, SoTA ML is high
            # Use method name to determine classification (more reliable)
            for i, method in enumerate(methods):
                val = df[df['Metric'] == metric_name][method].values[0]
                # Snort and Snort_Proposed are typically low values
                # SoTA_ML is typically high value
                if method in ['Snort', 'Snort_Proposed']:
                    low_values.append(val)
                    low_positions.append(positions[i])
                    low_methods.append((method, i))
                elif method == 'SoTA_ML':
                    high_values.append(val)
                    high_positions.append(positions[i])
                    high_methods.append((method, i))
                else:
                    # Fallback: use value-based threshold
                    threshold = sorted_vals[0] * 5
                    if val <= threshold:
                        low_values.append(val)
                        low_positions.append(positions[i])
                        low_methods.append((method, i))
                    else:
                        high_values.append(val)
                        high_positions.append(positions[i])
                        high_methods.append((method, i))
            
            if low_values and high_values:
                # Use broken axis (similar to Throughput)
                low_max = max(low_values)
                high_min = min(high_values)
                high_max = max(high_values)
                
                # Set y-axis range (similar to Throughput: 0-35 equivalent)
                # Scale to fit low values in lower part
                y_max = low_max * 2.5  # Equivalent to 35 in Throughput
                ax.set_ylim(0, y_max)
                
                # Plot low values in lower range
                for (method, orig_i), pos, val in zip(low_methods, low_positions, low_values):
                    ax.bar(
                        pos,
                        val,
                        width=bar_width,
                        label=method_display_names.get(method, method.replace('_', ' ')) if metric_name == 'Avg_Processing_Time' else '',
                        color=colors[method]
                    )
                    # Add text annotation
                    ax.text(pos, val + low_max * 0.05, f'{val:.1f}',
                           ha='center', va='bottom', fontsize=21, color=colors[method], weight='bold')
                
                # Find break position (similar to Throughput)
                low_max_pos = low_max
                high_start = low_max * 1.8  # Where high values start (equivalent to 27 in Throughput)
                break_position = (low_max_pos + high_start) / 2
                
                # Add break symbol
                add_break_symbol(ax, break_position, x_center=0.5, width=1.0)
                
                # Keep top spine visible
                ax.spines['top'].set_visible(True)
                
                # Plot high values scaled to fit above break (similar to Throughput)
                # Map from [high_min, high_max] to [high_start, high_start + 5]
                for (method, orig_i), pos, val in zip(high_methods, high_positions, high_values):
                    scaled_val = high_start + (val - high_min) / (high_max - high_min) * (y_max - high_start - 1)
                    # Add label for legend (only for first metric to avoid duplicates)
                    label_text = method_display_names.get(method, method.replace('_', ' ')) if metric_name == 'Avg_Processing_Time' else ''
                    ax.bar(
                        pos,
                        scaled_val,
                        width=bar_width,
                        label=label_text,
                        color=colors[method],
                        alpha=0.7
                    )
                    # Add text annotation with actual value
                    ax.text(pos, scaled_val + (y_max - high_start) * 0.05, f'{val:.1f}',
                           ha='center', va='bottom', fontsize=21, color=colors[method], weight='bold')
                
                # Set y-axis ticks for lower range
                ax.set_yticks([0, low_max * 0.5, low_max, low_max * 1.5, low_max * 2.0])
            else:
                # No clear separation, plot normally
                for i, method in enumerate(methods):
                    val = df[df['Metric'] == metric_name][method].values[0]
                    ax.bar(
                        positions[i],
                        val,
                        width=bar_width,
                        label=method_display_names.get(method, method.replace('_', ' ')) if metric_name == 'Avg_Processing_Time' else '',
                        color=colors[method]
                    )
                    ax.text(positions[i], val + max_val * 0.05, f'{val:.1f}',
                           ha='center', va='bottom', fontsize=21, color=colors[method], weight='bold')
                ax.set_ylim(0, max_val * 1.15 if max_val > 0 else 1)
        else:
            # No significant gap, plot normally
            for i, method in enumerate(methods):
                val = df[df['Metric'] == metric_name][method].values[0]
                ax.bar(
                    positions[i],
                    val,
                    width=bar_width,
                    label=method_display_names.get(method, method.replace('_', ' ')) if metric_name == 'Avg_Processing_Time' else '',
                    color=colors[method]
                )
                ax.text(positions[i], val + max_val * 0.05, f'{val:.1f}',
                       ha='center', va='bottom', fontsize=21, color=colors[method], weight='bold')
            ax.set_ylim(0, max_val * 1.15 if max_val > 0 else 1)
    
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
        'Snort_Proposed': '#27AE60',  # Green (will be displayed as "Snort + FlowSign")
        'SoTA_ML': '#3498DB'  # Blue
    }
    
    methods = ['Snort', 'Snort_Proposed', 'SoTA_ML']
    
    # Method display names
    method_display_names = {
        'Snort': 'Snort',
        'Snort_Proposed': 'Snort + FlowSign',
        'SoTA_ML': 'SoTA ML'
    }
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
        plot_metric(ax, df, metric_name, methods, colors, bar_width, method_display_names)
        
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

