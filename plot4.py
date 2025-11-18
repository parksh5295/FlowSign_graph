# subplot

import os
from pathlib import Path
import numpy as np

import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd

# Set font to Times New Roman (use serif family with Times New Roman as first choice)
mpl.rcParams["font.family"] = "serif"
mpl.rcParams["font.serif"] = ["Times New Roman", "Times", "DejaVu Serif", "Liberation Serif"]


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
                   ha='center', va='bottom', fontsize=56, color=colors[method], weight='bold')
        
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
        add_break_symbol(ax, break_position, x_center=0.5, width=1.4)
        
        # Keep top spine visible but it will be covered by the break symbol
        ax.spines['top'].set_visible(True)
        
        # Combine lower and upper ticks (gap between 15 and 27 shows the break)
        all_ticks = lower_ticks + high_tick_positions
        all_tick_labels = ['0', '5', '10', '15'] + [f'{int(t)}' for t in high_tick_values]
        
        # Set ticks and labels
        ax.set_yticks(all_ticks)
        ax.set_yticklabels(all_tick_labels, fontsize=72)  # Slightly reduced from original 24 for consistency
        
        # Plot high values scaled to fit in upper part of visible area
        # Map to the actual y-axis positions where ticks are located
        # high_tick_positions are at 27, 32, 37, 42... (5 units apart)
        # Map values to match these tick positions exactly
        for (method, orig_i), pos, val in zip(high_methods, high_positions, high_values):
            if num_ticks > 1:
                # Find the closest tick value and use its position
                # Interpolate between tick positions based on actual value
                # For example, if val=370.2 and ticks are [360, 365, 370, 375, 380]
                # Find which two ticks it's between and interpolate
                closest_idx = 0
                for i, tick_val in enumerate(high_tick_values):
                    if val >= tick_val:
                        closest_idx = i
                    else:
                        break
                
                # If value is exactly at a tick or beyond the last tick
                if closest_idx >= len(high_tick_positions) - 1:
                    scaled_val = high_tick_positions[-1]
                elif val == high_tick_values[closest_idx]:
                    scaled_val = high_tick_positions[closest_idx]
                else:
                    # Interpolate between two adjacent ticks
                    if closest_idx < len(high_tick_positions) - 1:
                        tick_val_low = high_tick_values[closest_idx]
                        tick_val_high = high_tick_values[closest_idx + 1]
                        pos_low = high_tick_positions[closest_idx]
                        pos_high = high_tick_positions[closest_idx + 1]
                        # Linear interpolation
                        ratio = (val - tick_val_low) / (tick_val_high - tick_val_low)
                        scaled_val = pos_low + ratio * (pos_high - pos_low)
                    else:
                        scaled_val = high_tick_positions[closest_idx]
            else:
                # Fallback to original scaling
                scaled_val = 27 + (val - high_min) / (high_max - high_min) * 5
            
            ax.bar(
                pos,
                scaled_val,
                width=bar_width,
                color=colors[method]
            )
            # Add text annotation with actual value (similar spacing to SoTA ML)
            # SoTA ML uses val + 0.5, so use scaled_val + 0.5 for similar spacing
            ax.text(pos, scaled_val + 0.5, f'{val:.1f}',
                       ha='center', va='bottom', fontsize=56, color=colors[method], weight='bold')
    else:
        # Plot normally (for Avg_Processing_Time and p95_Latency)
        # Use EXACT same approach as Throughput: separate low and high values
        positions = [x_center - bar_width, x_center, x_center + bar_width]
        
        # Separate low and high values (EXACT same logic as Throughput)
        # Low values: Snort and Snort+FlowSign (typically small)
        # High values: SoTA ML (typically large)
        low_values = []
        high_values = []
        low_positions = []
        high_positions = []
        low_methods = []
        high_methods = []
        
        # Classify by method name (same as Throughput logic)
        for i, method in enumerate(methods):
            val = df[df['Metric'] == metric_name][method].values[0]
            # Snort and Snort_Proposed are low values
            # SoTA_ML is high value
            if method == 'Snort' or method == 'Snort_Proposed':
                low_values.append(val)
                low_positions.append(positions[i])
                low_methods.append((method, i))
            elif method == 'SoTA_ML':
                high_values.append(val)
                high_positions.append(positions[i])
                high_methods.append((method, i))
        
        # Use broken axis if we have both low and high values (same as Throughput)
        if low_values and high_values:
            # Calculate ranges (similar to Throughput but dynamic)
            low_max = max(low_values) * 1.1  # Upper limit of lower range (with padding)
            high_min = min(high_values) * 0.9  # Lower limit of upper range (with padding)
            high_max = max(high_values) * 1.1  # Upper limit of upper range
            
            # Find break position (same as Throughput)
            low_max_val = max(low_values)
            # Use similar approach to Throughput: fixed range for low values
            # But make it larger to show bars more clearly, while keeping them below break
            # Set a reasonable upper limit for low range (similar to Throughput's 15)
            # Make it dynamic but ensure it doesn't exceed break position
            high_start = 27  # Where high values start (same as Throughput: 27)
            
            # Set low range end to be well below break (similar to Throughput's 15)
            # Use a value that makes bars visible but doesn't exceed break
            if low_max_val <= 1.0:
                low_range_end_val = 1.5  # Value range end
                tick_step = 0.5
            elif low_max_val <= 3.0:
                low_range_end_val = 4.0  # Value range end
                tick_step = 1.0
            elif low_max_val <= 5.0:
                low_range_end_val = 6.0  # Value range end
                tick_step = 1.5
            else:
                low_range_end_val = low_max_val * 1.2
                tick_step = round(low_max_val / 3)
            
            # Map low_range_end_val to y-axis position (similar to Throughput: 0-15 maps to 0-15)
            # But we want to keep it below break, so use a smaller range
            # Use position 0-20 for low values (similar to Throughput's 0-15)
            low_range_end_pos = 20  # Maximum y-axis position for low values (below break at 27)
            break_position = (low_range_end_pos + high_start) / 2  # Around 23.5
            
            # Create lower ticks with actual values (not scaled)
            # Map actual values to y-axis positions proportionally
            lower_ticks = []
            lower_tick_positions = []
            current_tick = 0
            
            while current_tick <= low_range_end_val:
                lower_ticks.append(current_tick)
                # Map value to y-axis position: 0 to low_range_end_val maps to 0 to low_range_end_pos
                pos = (current_tick / low_range_end_val) * low_range_end_pos if low_range_end_val > 0 else 0
                lower_tick_positions.append(pos)
                current_tick += tick_step
            
            # High value ticks: create ticks for high range
            # Use similar spacing logic as Throughput
            tick_range = high_max - high_min
            if tick_range > 0:
                # Create 4-5 ticks for high range
                num_high_ticks = 5
                high_tick_step = tick_range / (num_high_ticks - 1)
                high_tick_values = [high_min + i * high_tick_step for i in range(num_high_ticks)]
            else:
                high_tick_values = [high_min, high_max]
            
            # Map to y-axis positions with SAME VISUAL SPACING as lower ticks (same as Throughput)
            num_ticks = len(high_tick_values)
            if num_ticks > 1:
                # Use 27 to 27 + (num_ticks-1)*5 to maintain 5-unit visual spacing (same as Throughput)
                high_tick_positions = [27 + i * 5 for i in range(num_ticks)]
            else:
                high_tick_positions = [27]
            
            # Set y-axis range to accommodate upper ticks (same as Throughput)
            y_max = 27 + (num_ticks - 1) * 5 + 3 if num_ticks > 1 else 35
            ax.set_ylim(0, y_max)
            
            # Plot low values at actual positions (same as Throughput - no scaling)
            # Map actual values to y-axis positions proportionally
            for (method, orig_i), pos, val in zip(low_methods, low_positions, low_values):
                # Map actual value to y-axis position: 0 to low_range_end_val maps to 0 to low_range_end_pos
                y_pos = (val / low_range_end_val) * low_range_end_pos if low_range_end_val > 0 else 0
                ax.bar(
                    pos,
                    y_pos,
                    width=bar_width,
                    label=method_display_names.get(method, method.replace('_', ' ')) if metric_name == 'Avg_Processing_Time' else '',
                    color=colors[method]
                )
                # Add text annotation
                ax.text(pos, y_pos + low_range_end_pos * 0.05, f'{val:.1f}',
                       ha='center', va='bottom', fontsize=56, color=colors[method], weight='bold')
            
            # Add break symbol (same as Throughput)
            add_break_symbol(ax, break_position, x_center=0.5, width=1.4)
            
            # Keep top spine visible (same as Throughput)
            ax.spines['top'].set_visible(True)
            
            # Combine lower and upper ticks (same as Throughput)
            all_ticks = lower_tick_positions + high_tick_positions
            # Remove decimal points from y-axis labels
            all_tick_labels = [f'{int(t)}' for t in lower_ticks] + [f'{int(t)}' for t in high_tick_values]
            
            # Set ticks and labels (same as Throughput)
            ax.set_yticks(all_ticks)
            ax.set_yticklabels(all_tick_labels, fontsize=72)
            
            # Plot high values scaled to fit in upper part (EXACT same logic as Throughput)
            for (method, orig_i), pos, val in zip(high_methods, high_positions, high_values):
                if num_ticks > 1:
                    # Find the closest tick value and interpolate (EXACT same as Throughput)
                    closest_idx = 0
                    for i, tick_val in enumerate(high_tick_values):
                        if val >= tick_val:
                            closest_idx = i
                        else:
                            break
                    
                    # If value is exactly at a tick or beyond the last tick
                    if closest_idx >= len(high_tick_positions) - 1:
                        scaled_val = high_tick_positions[-1]
                    elif abs(val - high_tick_values[closest_idx]) < 0.01:  # Close enough to be considered equal
                        scaled_val = high_tick_positions[closest_idx]
                    else:
                        # Interpolate between two adjacent ticks
                        if closest_idx < len(high_tick_positions) - 1:
                            tick_val_low = high_tick_values[closest_idx]
                            tick_val_high = high_tick_values[closest_idx + 1]
                            pos_low = high_tick_positions[closest_idx]
                            pos_high = high_tick_positions[closest_idx + 1]
                            # Linear interpolation
                            ratio = (val - tick_val_low) / (tick_val_high - tick_val_low)
                            scaled_val = pos_low + ratio * (pos_high - pos_low)
                        else:
                            scaled_val = high_tick_positions[closest_idx]
                else:
                    # Fallback
                    scaled_val = 27 + (val - high_min) / (high_max - high_min) * 5
                
                # Add label for legend (same as Throughput)
                label_text = method_display_names.get(method, method.replace('_', ' ')) if metric_name == 'Avg_Processing_Time' else ''
                method_color = colors.get(method, '#000000')
                
                ax.bar(
                    pos,
                    scaled_val,
                    width=bar_width,
                    label=label_text,
                    color=method_color
                )
                # Add text annotation (same spacing as Throughput)
                ax.text(pos, scaled_val + 0.5, f'{val:.1f}',
                       ha='center', va='bottom', fontsize=56, color=colors[method], weight='bold')
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
                       ha='center', va='bottom', fontsize=56, color=colors[method], weight='bold')
            ax.set_ylim(0, max_val * 1.15 if max_val > 0 else 1)
            # Remove decimal points from y-axis for normal case
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x)}'))
    
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
    
    # Match plot1.py's figure size and font size ratios
    fig_width = 36  # Same as plot1.py
    fig, axes = plt.subplots(1, 3, figsize=(fig_width, 18))  # Reduced height
    fig.patch.set_facecolor('white')
    
    # Color scheme - unified dark colors
    colors = {
        'Snort': '#C0392B',  # Dark Red
        'Snort_Proposed': '#229954',  # Dark Green (will be displayed as "Snort + FlowSign")
        'SoTA_ML': '#2980B9'  # Dark Blue
    }
    
    methods = ['Snort', 'Snort_Proposed', 'SoTA_ML']
    
    # Method display names
    method_display_names = {
        'Snort': 'Snort',
        'Snort_Proposed': 'Snort + FlowSign',
        'SoTA_ML': 'BAE-UQ-IDS'
    }
    bar_width = 0.4  # Wider bars to fill the graph area
    
    # Metric names and y-axis labels (horizontal layout)
    metrics_info = [
        ('Avg_Processing_Time', 'Avg Processing Time (μs)', 0),
        ('p95_Latency', 'p95 Latency (μs)', 1),
        ('Throughput', 'Throughput (kpps)', 2)
    ]
    
    for metric_name, ylabel, idx in metrics_info:
        ax = axes[idx]
        ax.set_facecolor('white')
        
        # Plot metric with potential broken axis
        plot_metric(ax, df, metric_name, methods, colors, bar_width, method_display_names)
        
        ax.set_title(ylabel, fontsize=78)  # Use ylabel (which includes units) as title
        ax.tick_params(axis='y', labelsize=72)
        ax.grid(True, alpha=0.3, linestyle='--')
    
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
    
    # Debug: Check which methods are missing
    # If some methods are missing from legend, add them manually with correct colors
    for method in methods:
        display_name = method_display_names.get(method, method.replace('_', ' '))
        if display_name not in seen_labels:
            # Create a dummy handle with the correct color
            from matplotlib.patches import Rectangle
            # Use the actual color from colors dictionary
            method_color = colors.get(method, '#000000')
            dummy_handle = Rectangle((0, 0), 1, 1, facecolor=method_color, edgecolor='black')
            all_handles.append(dummy_handle)
            all_labels.append(display_name)
            seen_labels.add(display_name)
    
    fig.legend(all_handles, all_labels,
               loc='upper center',
               ncol=3,
               frameon=True,
               fontsize=76,  # Reduced font size
               bbox_to_anchor=(0.5, 1.03),  # Match plot1.py
               bbox_transform=fig.transFigure)
    
    fig.tight_layout(rect=[0.02, 0.01, 1, 0.90])  # Increased left margin
    
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

