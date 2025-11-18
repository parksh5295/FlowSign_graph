import os
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd

# Set font to Times New Roman (use serif family with Times New Roman as first choice)
mpl.rcParams["font.family"] = "serif"
mpl.rcParams["font.serif"] = ["Times New Roman", "Times", "DejaVu Serif", "Liberation Serif"]

def main():
    # CSV file path (relative to this script: ../Results/VPN_traffic.csv)
    base_dir = Path(__file__).resolve().parent
    csv_path = base_dir.parent / "Results" / "VPN_traffic.csv"

    # Avoid issues with minus sign rendering
    mpl.rcParams["axes.unicode_minus"] = False

    # Load data
    df = pd.read_csv(csv_path)

    datasets = df["Dataset"]

    # Bar positions
    x = range(len(datasets))
    # Adjust bar width based on number of datasets
    bar_width = 0.3 if len(datasets) > 2 else 0.35

    # A4 half-width size (A4 width = 8.27 inches, half = ~4 inches)
    # Increase figure size to accommodate larger text (similar to paper body text)
    fig_width = 36 if len(datasets) > 2 else 33  # Wider for larger text
    fig, axes = plt.subplots(1, 2, figsize=(fig_width, 10.8))  # Height reduced to 80% (13.5 * 0.8)
    fig.patch.set_facecolor('white')

    # ----- F1 Score subplot -----
    ax_f1 = axes[0]
    ax_f1.set_facecolor('white')
    ax_f1.bar(
        [i - bar_width / 2 for i in x],
        df["F1_snort"],
        width=bar_width,
        label="Snort",
        color="#C0392B",  # Dark Red for Snort
    )
    ax_f1.bar(
        [i + bar_width / 2 for i in x],
        df["F1_snort_FlowSign"],
        width=bar_width,
        label="Snort + FlowSign",
        color="#229954",  # Dark Green for Snort + FlowSign
    )
    ax_f1.set_title("F1 Score (%)", fontsize=83)
    ax_f1.set_xticks(list(x))
    ax_f1.set_xticklabels(datasets, fontsize=71, rotation=0, ha='center')
    ax_f1.tick_params(axis='x', pad=1)  # x축 레이블을 아래로 내림
    # y축 제목 제거
    # y축을 100 넘어가게 설정하되 y축 틱은 100까지만 표시
    ax_f1.set_ylim(0, 110)  # 100 넘어가게 설정
    ax_f1.tick_params(axis='y', labelsize=77)
    # y축 틱을 0-100까지만 표시 (100 넘어가는 값은 표기하지 않음)
    ax_f1.set_yticks(range(0, 101, 20))  # 0, 20, 40, 60, 80, 100만 표시
    ax_f1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x)}' if x <= 100 else ''))
    ax_f1.grid(True, alpha=0.3, linestyle='--')
    
    # 그래프 바 위에 값 표기
    for i in range(len(datasets)):
        # Snort 값
        snort_val = df["F1_snort"].iloc[i]
        ax_f1.text(i - bar_width / 2, snort_val + 0.2, f'{snort_val:.1f}',
                   ha='center', va='bottom', fontsize=44, color="#C0392B", weight='bold')
        # Snort + FlowSign 값
        flowsign_val = df["F1_snort_FlowSign"].iloc[i]
        ax_f1.text(i + bar_width / 2, flowsign_val + 0.2, f'{flowsign_val:.1f}',
                   ha='center', va='bottom', fontsize=44, color="#229954", weight='bold')

    # ----- Accuracy subplot -----
    ax_acc = axes[1]
    ax_acc.set_facecolor('white')
    ax_acc.bar(
        [i - bar_width / 2 for i in x],
        df["Accuracy_snort"],
        width=bar_width,
        label="Snort",
        color="#C0392B",  # Dark Red for Snort
    )
    ax_acc.bar(
        [i + bar_width / 2 for i in x],
        df["Accuracy_snort_FlowSign"],
        width=bar_width,
        label="Snort + FlowSign",
        color="#229954",  # Dark Green for Snort + FlowSign
    )
    ax_acc.set_title("Accuracy (%)", fontsize=83)
    ax_acc.set_xticks(list(x))
    ax_acc.set_xticklabels(datasets, fontsize=71, rotation=0, ha='center')
    ax_acc.tick_params(axis='x', pad=1)  # x축 레이블을 아래로 내림
    # y축을 100 넘어가게 설정하되 y축 틱은 100까지만 표시
    ax_acc.set_ylim(0, 110)  # 100 넘어가게 설정
    ax_acc.tick_params(axis='y', labelsize=77)
    # y축 틱을 0-100까지만 표시 (100 넘어가는 값은 표기하지 않음)
    ax_acc.set_yticks(range(0, 101, 20))  # 0, 20, 40, 60, 80, 100만 표시
    ax_acc.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x)}' if x <= 100 else ''))
    ax_acc.grid(True, alpha=0.3, linestyle='--')
    
    # 그래프 바 위에 값 표기
    for i in range(len(datasets)):
        # Snort 값
        snort_val = df["Accuracy_snort"].iloc[i]
        ax_acc.text(i - bar_width / 2, snort_val + 0.2, f'{snort_val:.1f}',
                   ha='center', va='bottom', fontsize=44, color="#C0392B", weight='bold')
        # Snort + FlowSign 값
        flowsign_val = df["Accuracy_snort_FlowSign"].iloc[i]
        ax_acc.text(i + bar_width / 2, flowsign_val + 0.2, f'{flowsign_val:.1f}',
                   ha='center', va='bottom', fontsize=44, color="#229954", weight='bold')

    # Add a single legend at the top center, above the graph area
    # Get handles and labels from one of the subplots
    handles, labels = ax_f1.get_legend_handles_labels()
    fig.legend(handles, labels, 
               loc='upper center', 
               ncol=2, 
               frameon=True,
               fontsize=81,
               bbox_to_anchor=(0.5, 1.055),  # 0.05 올림
               bbox_transform=fig.transFigure)
    
    # 높이가 80%로 줄어들었으므로 위쪽 여백 절대 크기 유지를 위해 top 값 조정
    # 원래: 높이 13.5, top=0.868 → 위쪽 여백 약 1.78
    # 현재: 높이 10.8, 같은 여백 유지 → top = 1 - (1.78/10.8) = 0.835
    fig.tight_layout(rect=[0, 0.01, 1, 0.829])

    # Output folder: ../Graph
    graph_dir = base_dir.parent / "Graph"
    os.makedirs(graph_dir, exist_ok=True)

    # Save image (e.g., ../Graph/vpn_traffic_performance.png)
    output_path = graph_dir / "vpn_traffic_performance.png"
    plt.savefig(output_path, dpi=300)

    # 화면에 표시
    plt.show()


if __name__ == "__main__":
    main()



