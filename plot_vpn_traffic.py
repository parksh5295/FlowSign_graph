import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


def main():
    # CSV 파일 경로 (이 스크립트 기준으로 ../Results/VPN_traffic.csv)
    csv_path = Path(__file__).resolve().parent.parent / "Results" / "VPN_traffic.csv"

    # 데이터 불러오기
    df = pd.read_csv(csv_path)

    # 그래프 스타일 설정
    plt.style.use("ggplot")

    datasets = df["Dataset"]

    # 막대 위치 설정
    x = range(len(datasets))
    bar_width = 0.35

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    # ----- F1 Score 그래프 -----
    ax_f1 = axes[0]
    ax_f1.bar(
        [i - bar_width / 2 for i in x],
        df["F1_snort"],
        width=bar_width,
        label="Snort",
        color="#4C72B0",
    )
    ax_f1.bar(
        [i + bar_width / 2 for i in x],
        df["F1_snort_FlowSign"],
        width=bar_width,
        label="Snort + FlowSign",
        color="#55A868",
    )
    ax_f1.set_title("F1 Score 비교")
    ax_f1.set_xticks(list(x))
    ax_f1.set_xticklabels(datasets)
    ax_f1.set_ylabel("F1 Score (%)")
    ax_f1.legend()

    # ----- Accuracy 그래프 -----
    ax_acc = axes[1]
    ax_acc.bar(
        [i - bar_width / 2 for i in x],
        df["Accuracy_snort"],
        width=bar_width,
        label="Snort",
        color="#C44E52",
    )
    ax_acc.bar(
        [i + bar_width / 2 for i in x],
        df["Accuracy_snort_FlowSign"],
        width=bar_width,
        label="Snort + FlowSign",
        color="#8172B3",
    )
    ax_acc.set_title("Accuracy 비교")
    ax_acc.set_xticks(list(x))
    ax_acc.set_xticklabels(datasets)
    ax_acc.set_ylabel("Accuracy (%)")
    ax_acc.legend()

    fig.suptitle("Snort vs Snort + FlowSign 성능 비교", fontsize=14, fontweight="bold")
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])

    # 이미지 파일로도 저장
    output_path = Path(__file__).resolve().parent / "vpn_traffic_performance.png"
    plt.savefig(output_path, dpi=300)

    # 화면에 표시
    plt.show()


if __name__ == "__main__":
    main()


