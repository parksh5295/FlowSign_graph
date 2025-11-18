import os
from pathlib import Path
import numpy as np

import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd

# Set font to Times New Roman (use serif family with Times New Roman as first choice)
mpl.rcParams["font.family"] = "serif"
mpl.rcParams["font.serif"] = ["Times New Roman", "Times", "DejaVu Serif", "Liberation Serif"]


def add_break_symbol(ax, y_break_pos, x_center=0.5, width=1.4):
    """Add a double wavy break symbol (~~~~) with white fill inside to indicate axis break."""
    from matplotlib.patches import Polygon
    
    # Create two wavy lines (double line, parallel)
    x_data = np.linspace(x_center - width/2, x_center + width/2, 200)
    y_range = ax.get_ylim()[1] - ax.get_ylim()[0]
    
    # Common wave pattern (same amplitude for parallel lines)
    wave_pattern = 0.01 * y_range * np.sin(15 * np.pi * (x_data - (x_center - width/2)) / width)
    
    # First wavy line (outer, upper) - parallel to second line
    y_data1 = y_break_pos + 0.025 * y_range + wave_pattern
    
    # Second wavy line (inner, lower) - parallel to first line
    y_data2 = y_break_pos + 0.0025 * y_range + wave_pattern
    
    # Create polygon path for white fill between the two wavy lines
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


def plot_metric_subplot(ax, df, metric_mean_name, metric_max_name, methods, method_columns, 
                        color_map, default_color, method_display_names, bar_width, title, 
                        break_type='none'):
    """Plot a single metric subplot with Mean bars and Max horizontal lines, with optional broken axis."""
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
    
    # Get all values
    mean_values = []
    max_values = []
    for i, method in enumerate(methods):
        method_col = method_columns[i]
        mean_val = mean_row[method_col].values[0]
        mean_values.append(mean_val)
        
        if metric_max_name:
            max_row = df[df['Metric'] == metric_max_name]
            if len(max_row) > 0:
                max_val = max_row[method_col].values[0]
                max_values.append(max_val)
            else:
                max_values.append(None)
        else:
            max_values.append(None)
    
    # Determine which method is BAE-UQ-IDS (usually the last one or contains 'BAE')
    bae_idx = None
    for i, method in enumerate(methods):
        if 'BAE' in method or method == method_columns[-1]:
            bae_idx = i
            break
    
    if break_type == 'duration':
        # Duration: Snort, Snort+FlowSign (low) / BAE (high)
        if bae_idx is not None:
            low_values = [(i, mean_values[i], positions[i]) for i in range(num_methods) if i != bae_idx]
            high_values = [(bae_idx, mean_values[bae_idx], positions[bae_idx])]
            
            # Low range: 0 to max of low values * 1.2
            low_max = max([v[1] for v in low_values]) * 1.2
            low_range_end_pos = 20
            high_start = 27
            break_position = (low_range_end_pos + high_start) / 2
            
            # Lower ticks
            tick_step = max(1, int(low_max / 5))
            lower_ticks = list(range(0, int(low_max) + tick_step, tick_step))
            lower_tick_positions = [i * 5 for i in range(len(lower_ticks))]
            
            # High ticks
            high_val = high_values[0][1]
            high_max = high_val * 1.1
            high_tick_values = [int(high_val), int(high_max)]
            high_tick_positions = [27, 32]
            
            # Plot low values
            for idx, val, pos in low_values:
                y_pos = (val / low_max) * low_range_end_pos if low_max > 0 else 0
                display_name = method_display_names.get(methods[idx], methods[idx].replace('_', ' ').replace('-', ' '))
                color = color_map.get(methods[idx], default_color)
                ax.bar(pos, y_pos, width=bar_width, 
                      label=display_name if metric_mean_name == 'Duration(s)' else '', 
                      color=color)
            
            # Plot high value
            if high_values:
                idx, val, pos = high_values[0]
                scaled_val = 27 + (val - high_tick_values[0]) / (high_tick_values[1] - high_tick_values[0]) * 5
                display_name = method_display_names.get(methods[idx], methods[idx].replace('_', ' ').replace('-', ' '))
                color = color_map.get(methods[idx], default_color)
                ax.bar(pos, scaled_val, width=bar_width, 
                      label=display_name if metric_mean_name == 'Duration(s)' else '', 
                      color=color)
            
            # Add break symbol
            add_break_symbol(ax, break_position, x_center=0.5, width=1.4)
            ax.spines['top'].set_visible(True)
            
            # Set ticks
            all_ticks = lower_tick_positions + high_tick_positions
            all_tick_labels = [f'{int(t)}' for t in lower_ticks] + [f'{int(t)}' for t in high_tick_values]
            ax.set_yticks(all_ticks)
            ax.set_yticklabels(all_tick_labels, fontsize=72)
            ax.set_ylim(0, 35)
        else:
            # No break needed
            for i, method in enumerate(methods):
                display_name = method_display_names.get(method, method.replace('_', ' ').replace('-', ' '))
                color = color_map.get(method, default_color)
                ax.bar(positions[i], mean_values[i], width=bar_width,
                      label=display_name if metric_mean_name == 'Duration(s)' else '', 
                      color=color)
            ax.set_ylim(0, max(mean_values) * 1.15)
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x)}'))
    
    elif break_type == 'cpu':
        # CPU: BAE-UQ-IDS max값만 high로 분리
        if bae_idx is not None and max_values[bae_idx] is not None:
            # All mean values in low range
            low_max = max(mean_values) * 1.2
            low_range_end_pos = 20
            high_start = 27
            break_position = (low_range_end_pos + high_start) / 2
            
            # Lower ticks
            tick_step = max(10, int(low_max / 5))
            lower_ticks = list(range(0, int(low_max) + tick_step, tick_step))
            lower_tick_positions = [i * 5 for i in range(len(lower_ticks))]
            
            # High ticks for BAE max
            bae_max_val = max_values[bae_idx]
            high_max = bae_max_val * 1.1
            high_tick_values = [int(bae_max_val * 0.9), int(bae_max_val), int(high_max)]
            high_tick_positions = [27, 30, 33]
            
            # Plot all mean values in low range
            for i, method in enumerate(methods):
                y_pos = (mean_values[i] / low_max) * low_range_end_pos if low_max > 0 else 0
                display_name = method_display_names.get(method, method.replace('_', ' ').replace('-', ' '))
                color = color_map.get(method, default_color)
                ax.bar(positions[i], y_pos, width=bar_width,
                      label=display_name if metric_mean_name == 'CPU_Mean(%)' else '', 
                      color=color)
            
            # Plot BAE max in high range
            scaled_max = 27 + (bae_max_val - high_tick_values[0]) / (high_tick_values[-1] - high_tick_values[0]) * 6
            x_start = positions[bae_idx] - bar_width / 2
            x_end = positions[bae_idx] + bar_width / 2
            ax.plot([x_start, x_end], [scaled_max, scaled_max], 'r--', linewidth=6, 
                   label='Max' if metric_mean_name == 'CPU_Mean(%)' else '', zorder=10)
            
            # Plot other max values in low range
            for i, method in enumerate(methods):
                if i != bae_idx and max_values[i] is not None:
                    max_val = max_values[i]
                    y_pos = (max_val / low_max) * low_range_end_pos if low_max > 0 else 0
                    x_start = positions[i] - bar_width / 2
                    x_end = positions[i] + bar_width / 2
                    ax.plot([x_start, x_end], [y_pos, y_pos], 'r--', linewidth=6, zorder=10)
            
            # Add break symbol
            add_break_symbol(ax, break_position, x_center=0.5, width=1.4)
            ax.spines['top'].set_visible(True)
            
            # Set ticks
            all_ticks = lower_tick_positions + high_tick_positions
            all_tick_labels = [f'{int(t)}' for t in lower_ticks] + [f'{int(t)}' for t in high_tick_values]
            ax.set_yticks(all_ticks)
            ax.set_yticklabels(all_tick_labels, fontsize=72)
            ax.set_ylim(0, 36)
        else:
            # No break needed
            for i, method in enumerate(methods):
                display_name = method_display_names.get(method, method.replace('_', ' ').replace('-', ' '))
                color = color_map.get(method, default_color)
                ax.bar(positions[i], mean_values[i], width=bar_width,
                      label=display_name if metric_mean_name == 'CPU_Mean(%)' else '', 
                      color=color)
                if max_values[i] is not None:
                    x_start = positions[i] - bar_width / 2
                    x_end = positions[i] + bar_width / 2
                    ax.plot([x_start, x_end], [max_values[i], max_values[i]], 'r--', linewidth=6, 
                           label='Max' if i == 0 and metric_mean_name == 'CPU_Mean(%)' else '', zorder=10)
            ax.set_ylim(0, max(max(mean_values), max([v for v in max_values if v is not None])) * 1.15)
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x)}'))
    
    elif break_type == 'memory':
        # Memory: 물결 2쌍 - BAE max(super high), BAE 막대(high), 나머지(low)
        if bae_idx is not None:
            # Low: Snort, Snort+FlowSign mean and max
            low_mean_values = [(i, mean_values[i], positions[i]) for i in range(num_methods) if i != bae_idx]
            low_max_values = [(i, max_values[i], positions[i]) for i in range(num_methods) 
                            if i != bae_idx and max_values[i] is not None]
            
            # High: BAE mean
            bae_mean_val = mean_values[bae_idx]
            bae_mean_pos = positions[bae_idx]
            
            # Super high: BAE max
            bae_max_val = max_values[bae_idx] if max_values[bae_idx] is not None else None
            
            # First break: low to high (BAE mean)
            low_max = max([v[1] for v in low_mean_values] + [v[1] for v in low_max_values]) * 1.2
            low_range_end_pos = 20
            high_start = 27
            break1_position = (low_range_end_pos + high_start) / 2
            
            # Second break: high to super high (BAE max)
            if bae_max_val:
                high_max = bae_mean_val * 1.2
                high_range_end_pos = 35
                super_high_start = 42
                break2_position = (high_range_end_pos + super_high_start) / 2
                
                # Super high ticks
                super_high_max = bae_max_val * 1.1
                super_high_tick_values = [int(bae_max_val * 0.95), int(bae_max_val), int(super_high_max)]
                super_high_tick_positions = [42, 45, 48]
            else:
                high_range_end_pos = 35
                super_high_start = None
                break2_position = None
            
            # Lower ticks
            tick_step = max(10, int(low_max / 5))
            lower_ticks = list(range(0, int(low_max) + tick_step, tick_step))
            lower_tick_positions = [i * 5 for i in range(len(lower_ticks))]
            
            # High ticks (for BAE mean)
            high_tick_values = [int(bae_mean_val * 0.9), int(bae_mean_val), int(bae_mean_val * 1.1)]
            high_tick_positions = [27, 30, 33]
            
            # Plot low mean values
            for idx, val, pos in low_mean_values:
                y_pos = (val / low_max) * low_range_end_pos if low_max > 0 else 0
                display_name = method_display_names.get(methods[idx], methods[idx].replace('_', ' ').replace('-', ' '))
                color = color_map.get(methods[idx], default_color)
                ax.bar(pos, y_pos, width=bar_width,
                      label=display_name if metric_mean_name == 'Memory_Mean(MB)' else '', 
                      color=color)
            
            # Plot low max values
            for idx, val, pos in low_max_values:
                y_pos = (val / low_max) * low_range_end_pos if low_max > 0 else 0
                x_start = pos - bar_width / 2
                x_end = pos + bar_width / 2
                ax.plot([x_start, x_end], [y_pos, y_pos], 'r--', linewidth=6, zorder=10)
            
            # Plot BAE mean in high range
            scaled_bae_mean = 27 + (bae_mean_val - high_tick_values[0]) / (high_tick_values[-1] - high_tick_values[0]) * 6
            display_name = method_display_names.get(methods[bae_idx], methods[bae_idx].replace('_', ' ').replace('-', ' '))
            color = color_map.get(methods[bae_idx], default_color)
            ax.bar(bae_mean_pos, scaled_bae_mean, width=bar_width,
                  label=display_name if metric_mean_name == 'Memory_Mean(MB)' else '', 
                  color=color)
            
            # Plot BAE max in super high range
            if bae_max_val:
                scaled_bae_max = 42 + (bae_max_val - super_high_tick_values[0]) / (super_high_tick_values[-1] - super_high_tick_values[0]) * 6
                x_start = bae_mean_pos - bar_width / 2
                x_end = bae_mean_pos + bar_width / 2
                ax.plot([x_start, x_end], [scaled_bae_max, scaled_bae_max], 'r--', linewidth=6, 
                       label='Max' if metric_mean_name == 'Memory_Mean(MB)' else '', zorder=10)
            
            # Add break symbols
            add_break_symbol(ax, break1_position, x_center=0.5, width=1.4)
            if break2_position:
                add_break_symbol(ax, break2_position, x_center=0.5, width=1.4)
            ax.spines['top'].set_visible(True)
            
            # Set ticks
            if bae_max_val:
                all_ticks = lower_tick_positions + high_tick_positions + super_high_tick_positions
                all_tick_labels = ([f'{int(t)}' for t in lower_ticks] + 
                                 [f'{int(t)}' for t in high_tick_values] + 
                                 [f'{int(t)}' for t in super_high_tick_values])
                ax.set_ylim(0, 51)
            else:
                all_ticks = lower_tick_positions + high_tick_positions
                all_tick_labels = [f'{int(t)}' for t in lower_ticks] + [f'{int(t)}' for t in high_tick_values]
                ax.set_ylim(0, 36)
            ax.set_yticks(all_ticks)
            ax.set_yticklabels(all_tick_labels, fontsize=72)
        else:
            # No break needed
            for i, method in enumerate(methods):
                display_name = method_display_names.get(method, method.replace('_', ' ').replace('-', ' '))
                color = color_map.get(method, default_color)
                ax.bar(positions[i], mean_values[i], width=bar_width,
                      label=display_name if metric_mean_name == 'Memory_Mean(MB)' else '', 
                      color=color)
                if max_values[i] is not None:
                    x_start = positions[i] - bar_width / 2
                    x_end = positions[i] + bar_width / 2
                    ax.plot([x_start, x_end], [max_values[i], max_values[i]], 'r--', linewidth=6, 
                           label='Max' if i == 0 and metric_mean_name == 'Memory_Mean(MB)' else '', zorder=10)
            ax.set_ylim(0, max(max(mean_values), max([v for v in max_values if v is not None])) * 1.15)
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x)}'))
    
    else:
        # No break - normal plotting
        for i, method in enumerate(methods):
            display_name = method_display_names.get(method, method.replace('_', ' ').replace('-', ' '))
            color = color_map.get(method, default_color)
            ax.bar(positions[i], mean_values[i], width=bar_width,
                  label=display_name if metric_mean_name == 'Duration(s)' else '', 
                  color=color)
            if max_values[i] is not None:
                x_start = positions[i] - bar_width / 2
                x_end = positions[i] + bar_width / 2
                ax.plot([x_start, x_end], [max_values[i], max_values[i]], 'r--', linewidth=6, 
                       label='Max' if i == 0 and metric_mean_name == 'Duration(s)' else '', zorder=10)
        ax.set_ylim(0, max(max(mean_values), max([v for v in max_values if v is not None] or [0])) * 1.15)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x)}'))
    
    # Set title and formatting
    ax.set_title(title, fontsize=78)
    ax.set_xticks([])  # No x-axis labels for individual subplots
    ax.tick_params(axis='y', labelsize=72)
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
    
    # Metric names and titles with break types
    metrics_info = [
        ('Duration(s)', None, 'Duration (s)', 0, 'duration'),  # Snort/Snort+FlowSign / BAE
        ('CPU_Mean(%)', 'CPU_Max(%)', 'CPU (%)', 1, 'cpu'),  # BAE max만 high
        ('Memory_Mean(MB)', 'Memory_Max(MB)', 'Memory (MB)', 2, 'memory')  # 물결 2쌍
    ]
    
    for metric_mean_name, metric_max_name, title, idx, break_type in metrics_info:
        ax = axes[idx]
        ax.set_facecolor('white')
        
        plot_metric_subplot(ax, df, metric_mean_name, metric_max_name, methods, method_columns,
                           color_map, default_color, method_display_names, bar_width, title, break_type)
    
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
    
    # Separate method handles and Max handle
    method_handles = []
    method_labels = []
    max_handle = None
    max_label = None
    
    for handle, label in zip(all_handles, all_labels):
        if label == 'Max':
            max_handle = handle
            max_label = label
        else:
            method_handles.append(handle)
            method_labels.append(label)
    
    # Create legend in 2 rows: methods on top, Max below
    if max_handle:
        # First row: methods (higher up)
        legend1 = fig.legend(method_handles, method_labels,
                            loc='upper center',
                            ncol=len(method_handles),
                            frameon=True,
                            fontsize=76,
                            bbox_to_anchor=(0.5, 1.06),
                            bbox_transform=fig.transFigure)
        
        # Second row: Max (lower, with more spacing)
        legend2 = fig.legend([max_handle], [max_label],
                            loc='upper center',
                            ncol=1,
                            frameon=True,
                            fontsize=76,
                            bbox_to_anchor=(0.5, 0.97),
                            bbox_transform=fig.transFigure)
    else:
        fig.legend(all_handles, all_labels,
                   loc='upper center',
                   ncol=len(all_handles),
                   frameon=True,
                   fontsize=76,
                   bbox_to_anchor=(0.5, 1.06),
                   bbox_transform=fig.transFigure)
    
    fig.tight_layout(rect=[0.02, 0.01, 1, 0.88])  # Increased top margin to prevent legend cutoff
    
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
