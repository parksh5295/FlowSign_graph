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
    ax.plot([x_data[0], x_data[0]], [y_data1[0], y_data2[0]], 
            'k-', linewidth=3, clip_on=False, zorder=15)
    ax.plot([x_data[-1], x_data[-1]], [y_data1[-1], y_data2[-1]], 
            'k-', linewidth=3, clip_on=False, zorder=15)


def main():
    # Base directory
    base_dir = Path(__file__).resolve().parent
    results_dir = base_dir.parent / "Results"
    
    # Avoid issues with minus sign rendering
    mpl.rcParams["axes.unicode_minus"] = False
    
    # Load result2.csv
    df = pd.read_csv(results_dir / "result2.csv")
    
    # Match plot1.py's figure size and font size ratios
    fig_width = 36  # Same as plot1.py
    fig, ax = plt.subplots(1, 1, figsize=(fig_width, 13.5))  # Height reduced to 75%
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
        'SoTA_ML': 'BAE-UQ-IDS'
    }
    
    # Check if we need broken axis (if max value is much larger than min non-zero value)
    all_values = []
    for metric in metrics:
        metric_df = df[df['Metric'] == metric]
        if len(metric_df) > 0:
            for method in methods:
                val = metric_df[method].values[0]
                if val > 0:
                    all_values.append(val)
    
    needs_break = False
    if len(all_values) > 1:
        max_val = max(all_values)
        min_val = min(all_values)
        if max_val > 0 and min_val > 0 and max_val / min_val > 3:
            needs_break = True
    
    if needs_break:
        # Use broken axis approach
        low_max = 50  # Upper limit of lower range
        high_min = 90  # Lower limit of upper range
        low_range_end_pos = 20
        high_start = 27
        break_position = (low_range_end_pos + high_start) / 2
        
        # 그래프의 x축 범위를 먼저 고정하여 막대 위치가 변하지 않도록 함
        ax.set_xlim(-0.5, len(metrics) - 0.5)
        
        # Plot bars with broken axis
        for metric_idx, metric in enumerate(metrics):
            metric_df = df[df['Metric'] == metric]
            if len(metric_df) > 0:
                for i, method in enumerate(methods):
                    val = metric_df[method].values[0]
                    if val <= low_max:
                        # Plot in lower range
                        y_pos = (val / low_max) * low_range_end_pos if low_max > 0 else 0
                        ax.bar(positions[i][metric_idx], y_pos, width=bar_width,
                              label=method_display_names.get(method, method.replace('_', ' ')) if metric_idx == 0 else '',
                              color=colors[method])
                    else:
                        # Plot in upper range (scaled)
                        scaled_val = high_start + (val - high_min) / (100 - high_min) * 8
                        ax.bar(positions[i][metric_idx], scaled_val, width=bar_width,
                              label=method_display_names.get(method, method.replace('_', ' ')) if metric_idx == 0 else '',
                              color=colors[method])
        
        # Add break symbol (across the entire x-axis range - one long wavy line)
        # 전체 x축에 걸쳐 하나의 긴 물결을 그림
        # [물결 좌우 길이 조정] x_min, x_max 값을 조정하여 물결 길이 변경
        # x_data = np.linspace(x_min, x_max, 500)로 물결을 그리므로, 이 값들이 물결의 좌우 범위를 결정합니다
        # 더 넓게: x_min을 더 작게, x_max를 더 크게 설정
        # 더 좁게: x_min을 더 크게, x_max를 더 작게 설정
        # 주의: x축 범위는 이미 고정되어 있으므로, 물결만 그래프 영역 밖으로 확장됩니다 (clip_on=False)
        x_min = -0.5  # 좌측으로 더 넓히기 위해 -0.5에서 -1.0으로 변경
        x_max = len(metrics) - 0.5  # 우측으로 더 넓히기 위해 len(metrics) - 0.5에서 len(metrics) + 0.5로 변경
        x_center = (x_min + x_max) / 2
        width = x_max - x_min + 0.5  # 전체 x축 범위 + 여유
        
        # Create two wavy lines (double line, parallel) across entire x-axis
        from matplotlib.patches import Polygon
        x_data = np.linspace(x_min, x_max, 500)
        y_range = ax.get_ylim()[1] - ax.get_ylim()[0]
        
        # Common wave pattern (same amplitude for parallel lines)
        wave_pattern = 0.01 * y_range * np.sin(15 * np.pi * (x_data - x_min) / (x_max - x_min))
        
        # First wavy line (outer, upper) - parallel to second line
        y_data1 = break_position + 0.025 * y_range + wave_pattern
        
        # Second wavy line (inner, lower) - parallel to first line
        y_data2 = break_position + 0.0025 * y_range + wave_pattern
        
        # Create polygon path for white fill between the two wavy lines
        polygon_points = np.vstack([
            np.column_stack([x_data, y_data1]),  # Outer line forward
            np.column_stack([x_data[::-1], y_data2[::-1]])  # Inner line backward
        ])
        
        # Fill the area between the two wavy lines with white
        poly = Polygon(polygon_points, facecolor='white', edgecolor='none', zorder=13, transform=ax.transData)
        ax.add_patch(poly)
        
        # Draw the two wavy lines
        # [두께 조정] linewidth 값을 조정하여 물결 두께 변경 (더 두껍게: 값 증가)
        ax.plot(x_data, y_data1, 'k-', linewidth=7, clip_on=False, zorder=15)  # linewidth=3 -> 5로 증가
        ax.plot(x_data, y_data2, 'k-', linewidth=7, clip_on=False, zorder=15)  # linewidth=3 -> 5로 증가
        
        # Add small vertical lines at ends
        ax.plot([x_data[0], x_data[0]], [y_data1[0], y_data2[0]], 
                'k-', linewidth=5, clip_on=False, zorder=15)  # linewidth=3 -> 5로 증가
        ax.plot([x_data[-1], x_data[-1]], [y_data1[-1], y_data2[-1]], 
                'k-', linewidth=5, clip_on=False, zorder=15)  # linewidth=3 -> 5로 증가
        
        ax.spines['top'].set_visible(True)
        
        # Set y-axis ticks (100 위에 여유 공간 추가)
        lower_ticks = [0, 25, 50]
        lower_tick_positions = [0, 10, 20]
        high_ticks = [90, 100]
        high_tick_positions = [27, 35]
        # 100 위에 여유 공간을 주기 위해 ylim을 더 높게 설정
        ax.set_ylim(0, 40)  # 35 -> 40으로 증가
        
        all_ticks = lower_tick_positions + high_tick_positions
        all_tick_labels = [f'{int(t)}' for t in lower_ticks] + [f'{int(t)}' for t in high_ticks]
        ax.set_yticks(all_ticks)
        ax.set_yticklabels(all_tick_labels, fontsize=77)
        
        # x축 레이블을 그래프 위에 표시 (ylim 설정 후)
        y_max = ax.get_ylim()[1]
        for i, metric in enumerate(metrics):
            # F1 -> F1-score로 변경
            display_metric = 'F1-score' if metric == 'F1' else metric
            ax.text(i, y_max * 1.05, f'{display_metric} (%)', 
                   ha='center', va='bottom', fontsize=79, transform=ax.transData)
        # 기존 x축 레이블 숨기기
        ax.set_xticklabels([''] * len(metrics))
        
        # 각 막대 위에 값 표시
        for metric_idx, metric in enumerate(metrics):
            metric_df = df[df['Metric'] == metric]
            if len(metric_df) > 0:
                for i, method in enumerate(methods):
                    val = metric_df[method].values[0]
                    if val <= low_max:
                        # Lower range에 있는 경우
                        y_pos = (val / low_max) * low_range_end_pos if low_max > 0 else 0
                        text_y = y_pos + 1  # 막대 위에 표시
                        ax.text(positions[i][metric_idx], text_y, f'{val:.2f}',
                               ha='center', va='bottom', fontsize=48, color=colors[method], weight='bold')
                    else:
                        # Upper range에 있는 경우
                        scaled_val = high_start + (val - high_min) / (100 - high_min) * 8
                        text_y = scaled_val + 0.5  # 막대 위에 표시
                        ax.text(positions[i][metric_idx], text_y, f'{val:.2f}',
                               ha='center', va='bottom', fontsize=48, color=colors[method], weight='bold')
    else:
        # Normal plotting without broken axis
        for i, method in enumerate(methods):
            bars = ax.bar(
                positions[i],
                df[method],
                width=bar_width,
                label=method_display_names.get(method, method.replace('_', ' ')),
                color=colors[method]
            )
            # 각 막대 위에 값 표시
            for j, bar in enumerate(bars):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2., height,
                       f'{df[method].iloc[j]:.2f}',
                       ha='center', va='bottom', fontsize=48, color=colors[method], weight='bold')
        
        # 100 위에 여유 공간을 주기 위해 ylim 조정
        current_ylim = ax.get_ylim()
        ax.set_ylim(current_ylim[0], current_ylim[1] * 1.1)  # 10% 여유 공간 추가
        
        # x축 레이블을 그래프 위에 표시 (ylim 설정 후)
        y_max = ax.get_ylim()[1]
        for i, metric in enumerate(metrics):
            # F1 -> F1-score로 변경
            display_metric = 'F1-score' if metric == 'F1' else metric
            ax.text(i, y_max * 1.05, f'{display_metric} (%)', 
                   ha='center', va='bottom', fontsize=79, transform=ax.transData)
        # 기존 x축 레이블 숨기기
        ax.set_xticklabels([''] * len(metrics))
    
    # 그래프 제목과 y축 제목 제거
    # broken axis가 없는 경우에도 x축 레이블을 그래프 위에 표시
    if not needs_break:
        # x축 레이블을 그래프 위에 표시 (ylim 설정 후)
        y_max = ax.get_ylim()[1]
        for i, metric in enumerate(metrics):
            # F1 -> F1-score로 변경
            display_metric = 'F1-score' if metric == 'F1' else metric
            ax.text(i, y_max * 1.05, f'{display_metric} (%)', 
                   ha='center', va='bottom', fontsize=79, transform=ax.transData)
        # 기존 x축 레이블 숨기기
        ax.set_xticklabels([''] * len(metrics))
    
    ax.set_xticks(x)
    if not needs_break:
        ax.tick_params(axis='y', labelsize=77)
        # Remove decimal points from y-axis
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x)}'))
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Add legend at the top center, above the graph area
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels,
               loc='upper center',
               ncol=3,
               frameon=True,
               fontsize=81,  # Match plot1.py
               bbox_to_anchor=(0.5, 1.04),  # 조금 더 위로 올림
               bbox_transform=fig.transFigure)
    
    # 높이가 75%로 줄어들었으므로 위쪽 여백 절대 크기 유지를 위해 top 값 조정
    # 원래: 높이 18, top=0.89 → 위쪽 여백 1.98
    # 현재: 높이 13.5, 같은 여백 유지 → top = 1 - (1.98/13.5) = 0.853
    fig.tight_layout(rect=[0, 0.01, 1, 0.853])
    
    # Output folder: ../Graph
    graph_dir = base_dir.parent / "Graph"
    os.makedirs(graph_dir, exist_ok=True)
    
    # Save image
    output_path = graph_dir / "result2_performance.png"
    plt.savefig(output_path, dpi=300)
    plt.close()
    
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()

