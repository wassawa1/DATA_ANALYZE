"""感覚記憶 vs 順序記憶 の正答率（告知 / 未告知）の比較棒グラフ

縦軸: 正答率
横軸: 感覚記憶 (点数1-134), 順序記憶 (点数135-206)

出力: `outputs/感覚_vs_順序_memory_type_accuracy.png`
"""
import numpy as np
import matplotlib.pyplot as plt

from analysis_utils import (
    load_sheet,
    data_file_path,
    ensure_data_dir,
    output_file_path,
    save_figure,
    LEGEND_FONT_SIZE,
    ANNOTATION_FONT_SIZE,
)


def compute_group_mean_accuracy(df, cols):
    """指定した点数列群に対するデータフレーム全体の平均正答率と合計正解数・合計件数を返す。

    戻り値: (mean_float, total_correct, total_count)
    """
    cols_exist = [c for c in cols if c in df.columns]
    if len(cols_exist) == 0:
        raise ValueError("指定した点数列が見つかりませんでした: %s" % cols[:5])

    # 各参加者ごとの平均を算出し、参加者平均を返す
    per_person = df[cols_exist].mean(axis=1)
    mean_val = per_person.mean()

    # 合計正解数（セル内が 1/0 の想定）と合計のセル数（NA を除く）
    total_correct = df[cols_exist].sum().sum()
    total_count = df[cols_exist].notna().sum().sum()

    return mean_val, int(total_correct), int(total_count)


def main():
    ensure_data_dir()
    data_path = data_file_path("データ_edit.xlsx")

    df_win = load_sheet(data_path, sheet_name="告知")
    df_wo = load_sheet(data_path, sheet_name="未告知")

    sensory_cols = [f"点数{i}" for i in range(1, 135)]
    order_cols = [f"点数{i}" for i in range(135, 207)]

    win_sensory, win_sensory_n, win_sensory_d = compute_group_mean_accuracy(df_win, sensory_cols)
    win_order, win_order_n, win_order_d = compute_group_mean_accuracy(df_win, order_cols)

    wo_sensory, wo_sensory_n, wo_sensory_d = compute_group_mean_accuracy(df_wo, sensory_cols)
    wo_order, wo_order_n, wo_order_d = compute_group_mean_accuracy(df_wo, order_cols)

    groups = ["感覚記憶", "順序記憶"]
    x = np.arange(len(groups))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 6))

    bars1 = ax.bar(x - width / 2, [win_sensory, win_order], width, label="告知", color="C0")
    bars2 = ax.bar(x + width / 2, [wo_sensory, wo_order], width, label="未告知", color="C1")

    ax.set_xticks(x)
    ax.set_xticklabels(groups, rotation=30, ha="right")
    ax.set_ylim(0, 1)
    ax.set_ylabel("正答率")
    ax.set_title("感覚記憶 vs 順序記憶：告知/未告知 の平均正答率")

    ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=LEGEND_FONT_SIZE)
    fig.subplots_adjust(bottom=0.25, right=0.78)

    # 値ラベルを付ける（パーセントと分子/分母の形式）
    labels = [
        (win_sensory, win_sensory_n, win_sensory_d),
        (win_order, win_order_n, win_order_d),
    ]
    labels2 = [
        (wo_sensory, wo_sensory_n, wo_sensory_d),
        (wo_order, wo_order_n, wo_order_d),
    ]

    def format_label(mean, n, d):
        pct = mean * 100
        return f"{pct:.1f}% ({n}/{d})"

    for bar, lab in zip(bars1, labels):
        h = bar.get_height()
        ax.annotate(format_label(*lab), xy=(bar.get_x() + bar.get_width() / 2, h), xytext=(0, 6),
                    textcoords='offset points', ha='center', va='bottom', fontsize=max(6, ANNOTATION_FONT_SIZE-2))

    for bar, lab in zip(bars2, labels2):
        h = bar.get_height()
        ax.annotate(format_label(*lab), xy=(bar.get_x() + bar.get_width() / 2, h), xytext=(0, 6),
                    textcoords='offset points', ha='center', va='bottom', fontsize=max(6, ANNOTATION_FONT_SIZE-2))

    # 保存（出力ディレクトリは helper 内で作られる）
    save_figure(fig, "感覚_vs_順序_memory_type_accuracy.png", figsize=fig.get_size_inches())
    plt.show()


if __name__ == "__main__":
    main()
